"""
Onboarding endpoint for agent self-service registration
"""

import json
import os
from typing import Dict, Any

import requests
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.authtoken.models import Token

from control_plane.control_plane_adapter import HttpControlPlaneAdapter
from control_plane.executor_adapter import HttpExecutorAdapter
from control_plane.models import UserTenantMapping

User = get_user_model()


@csrf_exempt
@require_http_methods(["POST"])
def onboard_leadscoring(request):
    """
    POST /api/onboard/leadscoring
    
    Instant onboarding endpoint for agents.
    
    CRITICAL FIX #4: Creates tenant in Repo B FIRST (source of truth)
    STRUCTURAL UPGRADE #1: Creates Stripe customer immediately (via Repo C)
    
    Request body:
    {
        "agent_id": "openclaw-001",
        "email": "agent@example.com",
        "organization_name": "OpenClaw"  // Optional
    }
    
    Returns:
    {
        "onboarded": true,
        "tier": "free",
        "api_key": "abc123...",
        "tenant_uuid": "be1b7614-60ad-4e77-8661-cb4fcba9b314",
        "free_calls_remaining": 100,
        "instructions": {...},
        "upgrade_info": {...},
        "pricing": {...}
    }
    """
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse(
            {"ok": False, "error": "Invalid JSON", "code": "VALIDATION_ERROR"},
            status=400,
        )
    except Exception as e:
        import traceback
        print(f"[ONBOARD] Error parsing request: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse(
            {"ok": False, "error": f"Request parsing error: {str(e)}", "code": "INTERNAL_ERROR"},
            status=500,
        )
    
    try:
        # Validate required fields
        agent_id = body.get("agent_id", "").strip()
        email = body.get("email", "").strip()
        organization_name = body.get("organization_name", "").strip()
        
        if not agent_id:
            return JsonResponse(
                {"ok": False, "error": "agent_id is required", "code": "VALIDATION_ERROR"},
                status=400,
            )
        
        if not email:
            return JsonResponse(
                {"ok": False, "error": "email is required", "code": "VALIDATION_ERROR"},
                status=400,
            )
        
        # Step 1: Create tenant in Repo B FIRST (CRITICAL FIX #4)
        governance_url = os.environ.get('ACP_BASE_URL') or os.environ.get('GOVERNANCE_HUB_URL')
        kernel_api_key = os.environ.get('ACP_KERNEL_KEY')
        
        if not governance_url or not kernel_api_key:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "Onboarding service not configured. ACP_BASE_URL and ACP_KERNEL_KEY must be set.",
                    "code": "CONFIGURATION_ERROR",
                },
                status=500,
            )
        
        control_plane = HttpControlPlaneAdapter(
            platform_url=governance_url,
            kernel_api_key=kernel_api_key,
        )
        
        # Call Repo B to create tenant
        # Note: Supabase Edge Functions use folder name as path (tenants-create, not tenants/create)
        tenant_create_url = f"{governance_url}/functions/v1/tenants-create"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {kernel_api_key}',
        }
        
        tenant_payload = {
            'agent_id': agent_id,
            'email': email,
        }
        if organization_name:
            tenant_payload['organization_name'] = organization_name
        
        try:
            print(f"[ONBOARD] Creating tenant in Repo B: {agent_id}")
            response = requests.post(tenant_create_url, headers=headers, json=tenant_payload, timeout=10)
            response.raise_for_status()
            tenant_result = response.json()
            
            # Handle both {data: {...}} and direct response formats
            tenant_data = tenant_result.get('data', tenant_result)
            tenant_uuid = tenant_data.get('tenant_uuid') or tenant_data.get('tenant_id')
            
            if not tenant_uuid:
                raise Exception("Repo B did not return tenant_uuid")
            
            print(f"[ONBOARD] Tenant created: {tenant_uuid}")
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error') or error_msg
                except:
                    pass
            print(f"[ONBOARD] Failed to create tenant in Repo B: {error_msg}")
            return JsonResponse(
                {
                    "ok": False,
                    "error": f"Failed to create tenant: {error_msg}",
                    "code": "TENANT_CREATION_ERROR",
                },
                status=500,
            )
        
        # Step 2: Create Stripe customer via Repo C (STRUCTURAL UPGRADE #1)
        stripe_customer_id = None
        cia_url = os.environ.get('CIA_URL')
        cia_service_key = os.environ.get('CIA_SERVICE_KEY')
        
        if cia_url and cia_service_key:
            executor = HttpExecutorAdapter(
                cia_url=cia_url,
                cia_service_key=cia_service_key,
                cia_anon_key=os.environ.get('CIA_ANON_KEY'),
                kernel_id=os.environ.get('KERNEL_ID', 'leadscore-kernel'),
            )
            
            try:
                print(f"[ONBOARD] Creating Stripe customer for tenant: {tenant_uuid}")
                stripe_result = executor.execute(
                    endpoint=f"/api/tenants/{tenant_uuid}/stripe/customers.create",
                    params={
                        "email": email,
                        "metadata": {
                            "tenant_uuid": tenant_uuid,
                            "agent_id": agent_id,
                        }
                    },
                    tenant_id=tenant_uuid,
                )
                
                # Extract customer ID from response
                if isinstance(stripe_result.data, dict):
                    stripe_customer_id = stripe_result.data.get('id') or stripe_result.data.get('customer_id')
                elif isinstance(stripe_result.data, str):
                    stripe_customer_id = stripe_result.data
                
                print(f"[ONBOARD] Stripe customer created: {stripe_customer_id}")
                
                # Update tenant in Repo B with stripe_customer_id
                # This would require a Repo B endpoint to update tenant, or we can skip for now
                # and let Repo B handle it via webhook or separate update call
                
            except Exception as e:
                # Log but don't fail onboarding - Stripe customer can be created later
                print(f"[ONBOARD] Warning: Failed to create Stripe customer: {e}")
                print(f"[ONBOARD] Onboarding will continue, but payment setup will be required later")
        
        # Step 3: Create Django User and Token (API key)
        # Check if user already exists (by email or agent_id)
        user = None
        try:
            # Try to find existing user by email
            user = User.objects.filter(email=email).first()
            if not user:
                # Create new user
                username = f"agent_{agent_id}"[:150]  # Django username max length
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=None,  # No password needed for API-only access
                )
                print(f"[ONBOARD] Created Django user: {user.username}")
            else:
                print(f"[ONBOARD] Using existing Django user: {user.username}")
        except Exception as e:
            return JsonResponse(
                {
                    "ok": False,
                    "error": f"Failed to create user: {str(e)}",
                    "code": "USER_CREATION_ERROR",
                },
                status=500,
            )
        
        # Create or get API token
        token, created = Token.objects.get_or_create(user=user)
        api_key = token.key
        
        # Store tenant_uuid mapping for this user
        UserTenantMapping.objects.update_or_create(
            user=user,
            defaults={'tenant_uuid': tenant_uuid}
        )
        print(f"[ONBOARD] Stored tenant mapping: user={user.username} -> tenant_uuid={tenant_uuid}")
        
        # Step 4: Return credentials
        base_url = request.build_absolute_uri('/').rstrip('/')
        
        return JsonResponse({
            "ok": True,
            "onboarded": True,
            "tier": "free",
            "api_key": api_key,
            "tenant_uuid": tenant_uuid,
            "free_calls_remaining": 100,
            "instructions": {
                "required_fields": {
                    "agent_id": "Unique identifier for your agent (e.g., 'openclaw-001')",
                    "email": "Email address for billing and notifications (required)"
                },
                "optional_fields": {
                    "organization_name": "Name of your organization (optional, defaults to agent_id)"
                },
                "setup_steps": [
                    f"1. Save your tenant_uuid: {tenant_uuid}",
                    f"2. Save your API key: {api_key}",
                    f"3. Set ACP_TENANT_ID environment variable to: {tenant_uuid}",
                    "4. Use the api_key as X-API-Key header in all API requests",
                    "5. Call /api/manage with action: domain.leadscoring.questions.upsert_bulk"
                ],
                "example_request": {
                    "url": f"{base_url}/api/manage",
                    "headers": {
                        "X-API-Key": api_key,
                        "Content-Type": "application/json"
                    },
                    "body": {
                        "action": "domain.leadscoring.questions.upsert_bulk",
                        "params": {
                            "questions": [
                                {
                                    "field_name": "budget",
                                    "number": 1,
                                    "text": "What is your budget?",
                                    "type": "MC",
                                    "choices": [
                                        {"text": "$0-10k", "value": 1},
                                        {"text": "$10k-50k", "value": 2},
                                        {"text": "$50k+", "value": 3}
                                    ]
                                }
                            ]
                        }
                    }
                },
                "free_tier_info": {
                    "calls_included": 100,
                    "message": "First 100 calls are free. After that, add a payment method to continue."
                },
                "documentation_url": f"{base_url}/api-docs",
                "api_reference": {
                    "endpoint": f"{base_url}/api/manage",
                    "action": "domain.leadscoring.questions.upsert_bulk",
                    "required_fields": {
                        "field_name": "Unique identifier (letters, numbers, underscore only)",
                        "number": "Question number (must be >= 1, unique per owner)",
                        "text": "Question text (max 200 characters)",
                        "type": "Question type: MC (multiple choice), CH (choice), O (open), I (integer), S (slider), D (date)"
                    },
                    "choices_format": {
                        "description": "For MC/CH types, provide choices array with text and value",
                        "example": [
                            {"text": "Option 1", "value": 1},
                            {"text": "Option 2", "value": 2}
                        ]
                    }
                }
            },
            "upgrade_info": {
                "message": "First 100 calls are free. After that, add a payment method to continue.",
                "upgrade_url": f"{base_url}/api/upgrade/checkout?tenant={tenant_uuid}"
            },
            "pricing": {
                "per_call": 0.001,
                "currency": "USD",
                "billing_period": "monthly"
            }
        })
    except Exception as e:
        import traceback
        print(f"[ONBOARD] Unexpected error in onboarding: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse(
            {
                "ok": False,
                "error": f"Onboarding failed: {str(e)}",
                "code": "INTERNAL_ERROR",
            },
            status=500,
        )