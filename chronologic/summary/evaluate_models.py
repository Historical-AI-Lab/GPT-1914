# Code mostly by Claude. 

import json
import os
import openai
from collections import defaultdict
import time

# Initialize OpenAI client from credentials file
with open('credentials.txt', encoding='utf-8') as f:
    organization = f.readline().strip()
    api_key = f.readline().strip()
    
client = openai.OpenAI(organization=organization, api_key=api_key)

# Model identifiers
BASE_MODEL = "gpt-4.1-mini-2025-04-14"
FINETUNED_MODEL = "ft:gpt-4.1-mini-2025-04-14:tedunderwood::CbB93x2c"

def load_validation_data(filepath):
    """Load validation data from JSONL file."""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def get_model_prediction(client, model, messages, max_retries=3):
    """Get prediction from a model with retry logic."""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0  # Use 0 for consistent evaluation
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
    return None

def parse_json_response(response_text):
    """Parse JSON response and extract synopsis_present value."""
    try:
        # Try to parse the entire response as JSON
        data = json.loads(response_text)
        return data.get("synopsis_present", "").lower()
    except json.JSONDecodeError:
        # Try to find JSON in the response
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end > start:
            try:
                data = json.loads(response_text[start:end])
                return data.get("synopsis_present", "").lower()
            except:
                pass
    return None

def calculate_metrics(predictions, ground_truth):
    """Calculate precision, recall, and F1 score."""
    # Convert to binary (1 for 'y', 0 for 'n')
    true_positives = sum(1 for pred, gt in zip(predictions, ground_truth) 
                        if pred == 'y' and gt == 'y')
    false_positives = sum(1 for pred, gt in zip(predictions, ground_truth) 
                         if pred == 'y' and gt == 'n')
    false_negatives = sum(1 for pred, gt in zip(predictions, ground_truth) 
                         if pred == 'n' and gt == 'y')
    true_negatives = sum(1 for pred, gt in zip(predictions, ground_truth) 
                        if pred == 'n' and gt == 'n')
    
    # Calculate metrics
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = (true_positives + true_negatives) / len(predictions) if len(predictions) > 0 else 0
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'accuracy': accuracy,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'true_negatives': true_negatives,
        'false_negatives': false_negatives,
        'total': len(predictions)
    }

def evaluate_models(validation_file):
    """Main evaluation function."""
    print(f"Loading validation data from {validation_file}...")
    validation_data = load_validation_data(validation_file)
    print(f"Loaded {len(validation_data)} validation examples")
    
    # Extract ground truth
    ground_truth = []
    for item in validation_data:
        messages = item.get("messages", [])
        # Find the assistant's response
        for msg in messages:
            if msg["role"] == "assistant":
                gt_response = parse_json_response(msg["content"])
                ground_truth.append(gt_response)
                break
    
    print(f"\nGround truth labels: {len(ground_truth)} items")
    print(f"Distribution: y={ground_truth.count('y')}, n={ground_truth.count('n')}")
    
    # Evaluate both models
    results = {}
    
    for model_name, model_id in [("Base GPT-4.1-mini", BASE_MODEL), 
                                   ("Fine-tuned Model", FINETUNED_MODEL)]:
        print(f"\n{'='*60}")
        print(f"Evaluating {model_name}...")
        print(f"{'='*60}")
        
        predictions = []
        errors = 0
        
        for i, item in enumerate(validation_data):
            # Get the messages, excluding the assistant's response
            messages = [msg for msg in item.get("messages", []) if msg["role"] != "assistant"]
            
            try:
                # Get prediction
                response = get_model_prediction(client, model_id, messages)
                prediction = parse_json_response(response)
                
                if prediction is None:
                    print(f"Warning: Could not parse response for item {i+1}")
                    print(f"Response was: {response[:200]}")
                    errors += 1
                    prediction = "unknown"
                
                predictions.append(prediction)
                
                # Progress indicator
                if (i + 1) % 10 == 0:
                    print(f"Processed {i+1}/{len(validation_data)} examples...")
                    
            except Exception as e:
                print(f"Error on item {i+1}: {e}")
                predictions.append("error")
                errors += 1
        
        # Filter out errors and unknowns for metric calculation
        valid_indices = [i for i, pred in enumerate(predictions) 
                        if pred in ['y', 'n']]
        valid_predictions = [predictions[i] for i in valid_indices]
        valid_ground_truth = [ground_truth[i] for i in valid_indices]
        
        print(f"\nValid predictions: {len(valid_predictions)}/{len(predictions)}")
        print(f"Errors/unparseable: {errors}")
        
        # Calculate metrics
        metrics = calculate_metrics(valid_predictions, valid_ground_truth)
        results[model_name] = metrics
        
        # Print results
        print(f"\n{model_name} Results:")
        print(f"  Accuracy:  {metrics['accuracy']:.3f}")
        print(f"  Precision: {metrics['precision']:.3f}")
        print(f"  Recall:    {metrics['recall']:.3f}")
        print(f"  F1 Score:  {metrics['f1']:.3f}")
        print(f"\n  Confusion Matrix:")
        print(f"    True Positives:  {metrics['true_positives']}")
        print(f"    False Positives: {metrics['false_positives']}")
        print(f"    True Negatives:  {metrics['true_negatives']}")
        print(f"    False Negatives: {metrics['false_negatives']}")
    
    # Comparison
    print(f"\n{'='*60}")
    print("COMPARISON")
    print(f"{'='*60}")
    print(f"{'Metric':<15} {'Base Model':<15} {'Fine-tuned':<15} {'Improvement':<15}")
    print(f"{'-'*60}")
    
    base_results = results["Base GPT-4.1-mini"]
    ft_results = results["Fine-tuned Model"]
    
    for metric in ['accuracy', 'precision', 'recall', 'f1']:
        base_val = base_results[metric]
        ft_val = ft_results[metric]
        improvement = ft_val - base_val
        improvement_str = f"+{improvement:.3f}" if improvement >= 0 else f"{improvement:.3f}"
        print(f"{metric.capitalize():<15} {base_val:<15.3f} {ft_val:<15.3f} {improvement_str:<15}")
    
    return results

if __name__ == "__main__":
    import sys
    
    # Default file path
    validation_file = "fine_tuning_data_synopsis_detection_val.jsonl"
    
    # Allow file path as command line argument
    if len(sys.argv) > 1:
        validation_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(validation_file):
        print(f"Error: File '{validation_file}' not found.")
        print(f"Usage: python evaluate_models.py [validation_file.jsonl]")
        sys.exit(1)
    
    # Run evaluation
    results = evaluate_models(validation_file)
    
    print("\nEvaluation complete!")
