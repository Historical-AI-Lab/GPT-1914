# Motive/Behavior Scorer
# Compares model predictions against ground truth data
# Usage: python scorer.py <predictions_file> <ground_truth_file>
# Example: python scorer.py predictions.json ground_truth.json

import json
import sys
from difflib import SequenceMatcher

def fuzzy_match(a, b, threshold=0.5):
    """Check if two strings fuzzy match above threshold using SequenceMatcher"""
    if not a or not b:
        return False
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio() > threshold

def combine_motives_behaviors(gt_item):
    """Combine standalone and additional motives/behaviors into unified lists"""
    motives = []
    behaviors = []
    
    # Add standalone motive and behavior if they exist and are non-empty
    if gt_item.get('motive_passage', '').strip():
        motives.append(gt_item['motive_passage'].strip())
    if gt_item.get('behavior_passage', '').strip():
        behaviors.append(gt_item['behavior_passage'].strip())
    
    # Add additional motives and behaviors
    if 'more_motives' in gt_item and gt_item['more_motives']:
        for motive in gt_item['more_motives']:
            if motive.strip():
                motives.append(motive.strip())
    if 'more_behavior' in gt_item and gt_item['more_behavior']:
        for behavior in gt_item['more_behavior']:
            if behavior.strip():
                behaviors.append(behavior.strip())
    
    return motives, behaviors

def score_predictions(predictions, ground_truth):
    """Score predictions against ground truth"""
    if len(predictions) != len(ground_truth):
        print(f"Warning: Mismatched lengths - Predictions: {len(predictions)}, Ground truth: {len(ground_truth)}")
        min_len = min(len(predictions), len(ground_truth))
        predictions = predictions[:min_len]
        ground_truth = ground_truth[:min_len]
    
    # Y/N scoring variables
    correct_yn = 0
    predicted_y = 0
    actual_y = 0
    true_positives = 0
    
    # Passage matching scoring variables
    total_match_score = 0
    predicted_y_count = 0
    
    for i, (pred, gt) in enumerate(zip(predictions, ground_truth)):
        pred_yn = pred.get('motive_yn', '').lower().strip()
        gt_yn = gt.get('motive_yn', '').lower().strip()
        
        # Y/N accuracy
        if pred_yn == gt_yn:
            correct_yn += 1
        
        # Count for precision/recall
        if pred_yn == 'y':
            predicted_y += 1
            predicted_y_count += 1
        if gt_yn == 'y':
            actual_y += 1
        if pred_yn == 'y' and gt_yn == 'y':
            true_positives += 1
        
        # Passage matching (only for predicted 'y')
        if pred_yn == 'y':
            if gt_yn == 'n':
                # Ground truth is 'n', so no passages to match against
                # This prediction gets 0 points for passage matching
                continue
            
            # Get unified motive/behavior lists from ground truth
            gt_motives, gt_behaviors = combine_motives_behaviors(gt)
            
            pred_motive = pred.get('motive_passage', '').strip()
            pred_behavior = pred.get('behavior_passage', '').strip()
            
            # Debug output for first few items
            if i < 3:
                print(f"Chunk {i}: GT motives: {len(gt_motives)}, GT behaviors: {len(gt_behaviors)}")
                print(f"  Pred motive: '{pred_motive[:50]}...'")
                if gt_motives:
                    print(f"  GT motive 0: '{gt_motives[0][:50]}...'")
            
            # Check for motive match
            motive_matched_idx = None
            for j, gt_motive in enumerate(gt_motives):
                if fuzzy_match(pred_motive, gt_motive):
                    motive_matched_idx = j
                    total_match_score += 1
                    if i < 3:
                        print(f"    Motive match found at index {j}")
                    break
            
            # Check for corresponding behavior match
            if motive_matched_idx is not None and motive_matched_idx < len(gt_behaviors):
                corresponding_behavior = gt_behaviors[motive_matched_idx]
                if fuzzy_match(pred_behavior, corresponding_behavior):
                    total_match_score += 1
                    if i < 3:
                        print(f"    Behavior match found for index {motive_matched_idx}")
                elif i < 3:
                    print(f"    Behavior no match for index {motive_matched_idx}")
            elif i < 3 and motive_matched_idx is not None:
                print(f"    No corresponding behavior at index {motive_matched_idx}")
    
    # Calculate metrics
    accuracy = correct_yn / len(predictions) if len(predictions) > 0 else 0
    precision = true_positives / predicted_y if predicted_y > 0 else 0
    recall = true_positives / actual_y if actual_y > 0 else 0
    match_percentage = total_match_score / (2 * predicted_y_count) if predicted_y_count > 0 else 0
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'match_percentage': match_percentage,
        'total_predictions': len(predictions),
        'predicted_y': predicted_y,
        'actual_y': actual_y,
        'true_positives': true_positives,
        'total_match_score': total_match_score,
        'predicted_y_count': predicted_y_count
    }

def load_json_data(filename):
    """Load JSON data from file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_chunks(data):
    """Extract chunks list from JSON data, handling different structures"""
    # Check for 'results' field first (predictions format)
    if 'results' in data:
        return data['results']
    # Then check for 'chunks' field (ground truth format)
    elif 'chunks' in data:
        return data['chunks']
    # If it's already a list, return as is
    elif isinstance(data, list):
        return data
    else:
        raise ValueError("Could not find chunks in data structure")

def main():
    if len(sys.argv) != 3:
        print("Usage: python scorer.py <predictions_file> <ground_truth_file>")
        print("Example: python scorer.py predictions.json ground_truth.json")
        sys.exit(1)
    
    pred_file = sys.argv[1]
    gt_file = sys.argv[2]
    
    try:
        # Load data
        print("Loading prediction data...")
        pred_data = load_json_data(pred_file)
        print("Loading ground truth data...")
        gt_data = load_json_data(gt_file)
        
        # Extract chunks
        pred_chunks = extract_chunks(pred_data)
        gt_chunks = extract_chunks(gt_data)
        
        print(f"Loaded {len(pred_chunks)} prediction chunks and {len(gt_chunks)} ground truth chunks")
        
        # Score predictions
        results = score_predictions(pred_chunks, gt_chunks)
        
        # Print results
        print("\n" + "="*50)
        print("SCORING RESULTS")
        print("="*50)
        print(f"Y/N Classification:")
        print(f"  Accuracy:  {results['accuracy']:.3f} ({int(results['accuracy'] * results['total_predictions'])}/{results['total_predictions']} correct)")
        print(f"  Precision: {results['precision']:.3f} ({results['true_positives']}/{results['predicted_y']} predicted Y were correct)")
        print(f"  Recall:    {results['recall']:.3f} ({results['true_positives']}/{results['actual_y']} actual Y were predicted)")
        
        print(f"\nPassage Matching (for predicted Y chunks):")
        print(f"  Match Percentage: {results['match_percentage']:.3f}")
        print(f"  Match Score: {results['total_match_score']}/{2 * results['predicted_y_count']} possible points")
        print(f"  (Based on {results['predicted_y_count']} chunks predicted as Y)")
        
        print(f"\nSummary:")
        print(f"  Total chunks processed: {results['total_predictions']}")
        print(f"  Predicted Y: {results['predicted_y']}")
        print(f"  Actual Y: {results['actual_y']}")
        
    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()