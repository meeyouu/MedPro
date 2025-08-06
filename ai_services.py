"""
AI Service Integration Module
Handles OpenAI, Claude, Gemini, and OpenRouter connections
"""
import os
import json
import logging
from datetime import datetime
from openai import OpenAI
from anthropic import Anthropic
from google import genai
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_openai_connection(api_key, model='gpt-4o'):
    """Test OpenAI API connection"""
    try:
        if not api_key:
            return {'success': False, 'error': 'API key is required'}
        
        client = OpenAI(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Test connection. Respond with 'OK'."}],
            max_tokens=10,
            timeout=30
        )
        
        if response.choices and response.choices[0].message.content:
            return {
                'success': True, 
                'message': 'OpenAI connection successful',
                'model': model,
                'response': response.choices[0].message.content.strip()
            }
        else:
            return {'success': False, 'error': 'Invalid response from OpenAI'}
            
    except Exception as e:
        logger.error(f"OpenAI connection test failed: {str(e)}")
        return {'success': False, 'error': f'Connection failed: {str(e)}'}

def test_claude_connection(api_key, model='claude-sonnet-4-20250514'):
    """Test Claude API connection"""
    try:
        if not api_key:
            return {'success': False, 'error': 'API key is required'}
        
        client = Anthropic(api_key=api_key)
        
        # Test with a simple message
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Test connection. Respond with 'OK'."}]
        )
        
        if response.content and len(response.content) > 0:
            return {
                'success': True,
                'message': 'Claude connection successful',
                'model': model,
                'response': response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            }
        else:
            return {'success': False, 'error': 'Invalid response from Claude'}
            
    except Exception as e:
        logger.error(f"Claude connection test failed: {str(e)}")
        return {'success': False, 'error': f'Connection failed: {str(e)}'}

def test_gemini_connection(api_key, model='gemini-2.5-flash'):
    """Test Gemini API connection"""
    try:
        if not api_key:
            return {'success': False, 'error': 'API key is required'}
        
        client = genai.Client(api_key=api_key)
        
        # Test with a simple generation
        response = client.models.generate_content(
            model=model,
            contents="Test connection. Respond with 'OK'."
        )
        
        if response.text:
            return {
                'success': True,
                'message': 'Gemini connection successful',
                'model': model,
                'response': response.text.strip()
            }
        else:
            return {'success': False, 'error': 'Invalid response from Gemini'}
            
    except Exception as e:
        logger.error(f"Gemini connection test failed: {str(e)}")
        return {'success': False, 'error': f'Connection failed: {str(e)}'}

def test_openrouter_connection(api_key, model):
    """Test OpenRouter API connection"""
    try:
        if not api_key:
            return {'success': False, 'error': 'API key is required'}
        
        if not model:
            return {'success': False, 'error': 'Model selection is required for OpenRouter'}
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': 'Test connection. Respond with "OK".'}],
            'max_tokens': 10
        }
        
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return {
                    'success': True,
                    'message': 'OpenRouter connection successful',
                    'model': model,
                    'response': result['choices'][0]['message']['content'].strip()
                }
            else:
                return {'success': False, 'error': 'Invalid response format from OpenRouter'}
        else:
            return {'success': False, 'error': f'HTTP {response.status_code}: {response.text}'}
            
    except Exception as e:
        logger.error(f"OpenRouter connection test failed: {str(e)}")
        return {'success': False, 'error': f'Connection failed: {str(e)}'}

def generate_medical_analysis(patient_data, test_results, ai_service='openai', settings=None):
    """Generate comprehensive medical analysis using specified AI service"""
    try:
        # Prepare prompt for medical analysis
        prompt = f"""
        As a medical AI assistant, analyze the following patient data and laboratory results.
        Provide a comprehensive analysis in Persian (Farsi) with the following structure:

        Patient Information:
        {json.dumps(patient_data, indent=2, ensure_ascii=False)}

        Laboratory Results:
        {json.dumps(test_results, indent=2, ensure_ascii=False)}

        Please provide:
        1. Overall health assessment (ارزیابی کلی سلامت)
        2. Individual test analysis (تحلیل تک تک آزمایش‌ها)
        3. Probable conditions or diseases (احتمال بیماری‌ها)
        4. Clinical recommendations (توصیه‌های بالینی)
        5. Follow-up instructions (دستورالعمل‌های پیگیری)
        6. Red flags or critical findings (نشانه‌های خطر)

        Format response as JSON with Persian text.
        """
        
        if ai_service == 'openai' and settings and settings.openai_enabled:
            return _generate_with_openai(prompt, settings.openai_api_key, settings.openai_model)
        elif ai_service == 'claude' and settings and settings.claude_enabled:
            return _generate_with_claude(prompt, settings.claude_api_key, settings.claude_model)
        elif ai_service == 'gemini' and settings and settings.gemini_enabled:
            return _generate_with_gemini(prompt, settings.gemini_api_key, settings.gemini_model)
        elif ai_service == 'openrouter' and settings and settings.openrouter_enabled:
            return _generate_with_openrouter(prompt, settings.openrouter_api_key, settings.openrouter_model)
        else:
            return {'success': False, 'error': f'AI service {ai_service} is not enabled or configured'}
            
    except Exception as e:
        logger.error(f"Medical analysis generation failed: {str(e)}")
        return {'success': False, 'error': f'Analysis generation failed: {str(e)}'}

def _generate_with_openai(prompt, api_key, model):
    """Generate analysis using OpenAI"""
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=2000,
            temperature=0.7
        )
        
        if response.choices and response.choices[0].message.content:
            analysis = json.loads(response.choices[0].message.content)
            return {'success': True, 'analysis': analysis, 'service': 'openai'}
        else:
            return {'success': False, 'error': 'Invalid response from OpenAI'}
            
    except Exception as e:
        return {'success': False, 'error': f'OpenAI generation failed: {str(e)}'}

def _generate_with_claude(prompt, api_key, model):
    """Generate analysis using Claude"""
    try:
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": f"{prompt}\n\nPlease respond with valid JSON format."}]
        )
        
        if response.content and len(response.content) > 0:
            content = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            analysis = json.loads(content)
            return {'success': True, 'analysis': analysis, 'service': 'claude'}
        else:
            return {'success': False, 'error': 'Invalid response from Claude'}
            
    except Exception as e:
        return {'success': False, 'error': f'Claude generation failed: {str(e)}'}

def _generate_with_gemini(prompt, api_key, model):
    """Generate analysis using Gemini"""
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=f"{prompt}\n\nPlease respond with valid JSON format."
        )
        
        if response.text:
            analysis = json.loads(response.text)
            return {'success': True, 'analysis': analysis, 'service': 'gemini'}
        else:
            return {'success': False, 'error': 'Invalid response from Gemini'}
            
    except Exception as e:
        return {'success': False, 'error': f'Gemini generation failed: {str(e)}'}

def _generate_with_openrouter(prompt, api_key, model):
    """Generate analysis using OpenRouter"""
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': f"{prompt}\n\nPlease respond with valid JSON format."}],
            'max_tokens': 2000,
            'temperature': 0.7
        }
        
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                analysis = json.loads(content)
                return {'success': True, 'analysis': analysis, 'service': 'openrouter'}
            else:
                return {'success': False, 'error': 'Invalid response format from OpenRouter'}
        else:
            return {'success': False, 'error': f'HTTP {response.status_code}: {response.text}'}
            
    except Exception as e:
        return {'success': False, 'error': f'OpenRouter generation failed: {str(e)}'}