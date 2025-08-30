import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { questionsAPI } from '../config/api';

const QuestionForm = ({ question = null, onSuccess }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  
  const { register, handleSubmit, formState: { errors }, reset } = useForm({
    defaultValues: question || {
      number: '',
      text: '',
      field_name: '',
      type: 'CH',
      multiple_values: false,
      min_value: '',
      max_value: '',
    }
  });

  const questionTypes = [
    { value: 'O', label: 'Open' },
    { value: 'CH', label: 'Choices' },
    { value: 'MC', label: 'Multiple Choices' },
    { value: 'S', label: 'Slider' },
    { value: 'I', label: 'Integer' },
    { value: 'D', label: 'Date' },
  ];

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    setError(null);
    
    try {
      if (question) {
        // Update existing question
        await questionsAPI.update(question.id, data);
      } else {
        // Create new question
        await questionsAPI.create(data);
      }
      
      reset();
      onSuccess && onSuccess();
    } catch (err) {
      setError(err.response?.data || 'An error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6">
        {question ? 'Edit Question' : 'Create New Question'}
      </h2>
      
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {typeof error === 'object' ? JSON.stringify(error) : error}
        </div>
      )}
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Question Number
            </label>
            <input
              type="number"
              {...register('number', { required: 'Question number is required' })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.number && (
              <p className="text-red-500 text-sm mt-1">{errors.number.message}</p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Field Name
            </label>
            <input
              type="text"
              {...register('field_name', { 
                required: 'Field name is required',
                pattern: {
                  value: /^[a-zA-Z_][a-zA-Z0-9_]*$/,
                  message: 'Field name must start with a letter or underscore and contain only letters, numbers, and underscores'
                }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.field_name && (
              <p className="text-red-500 text-sm mt-1">{errors.field_name.message}</p>
            )}
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Question Text
          </label>
          <input
            type="text"
            {...register('text', { required: 'Question text is required' })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.text && (
            <p className="text-red-500 text-sm mt-1">{errors.text.message}</p>
          )}
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Question Type
          </label>
          <select
            {...register('type', { required: 'Question type is required' })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {questionTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
          {errors.type && (
            <p className="text-red-500 text-sm mt-1">{errors.type.message}</p>
          )}
        </div>
        
        <div className="flex items-center">
          <input
            type="checkbox"
            {...register('multiple_values')}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label className="ml-2 block text-sm text-gray-900">
            Allow multiple values
          </label>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Min Value (for Slider)
            </label>
            <input
              type="number"
              {...register('min_value')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Value (for Slider)
            </label>
            <input
              type="number"
              {...register('max_value')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        
        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={() => reset()}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Reset
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isSubmitting ? 'Saving...' : (question ? 'Update Question' : 'Create Question')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default QuestionForm;
