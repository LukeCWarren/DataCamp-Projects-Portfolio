import pandas as pd
import numpy as np

def merge_all_data(health_path, supplement_path, experiments_path, profiles_path):
    # Load data
    health = pd.read_csv(health_path)
    supplements = pd.read_csv(supplement_path)
    experiments = pd.read_csv(experiments_path)
    profiles = pd.read_csv(profiles_path)

    # Clean sleep_hours: strip 'h'/'H' suffix and convert to float
    health['sleep_hours'] = health['sleep_hours'].str.replace('[hH]', '', regex=True).astype(float)

    # Parse dates
    health['date'] = pd.to_datetime(health['date']).dt.date
    supplements['date'] = pd.to_datetime(supplements['date']).dt.date

    # Convert dosage to grams
    supplements['dosage_grams'] = supplements.apply(
        lambda r: r['dosage'] / 1000 if r['dosage_unit'] == 'mg' else r['dosage'], axis=1
    )

    # Merge supplements with experiments to get experiment_name
    supplements = supplements.merge(
        experiments[['experiment_id', 'name']].rename(columns={'name': 'experiment_name'}),
        on='experiment_id', how='left'
    )

    # Merge health with supplements (left join - keep all health rows)
    merged = health.merge(
        supplements[['user_id', 'date', 'supplement_name', 'dosage_grams', 'is_placebo', 'experiment_name']],
        on=['user_id', 'date'], how='left'
    )

    # Fill missing supplement_name with 'No intake'
    merged['supplement_name'] = merged['supplement_name'].fillna('No intake')

    # Create age group bins
    def age_group(age):
        if pd.isna(age):
            return 'Unknown'
        age = int(age)
        if age < 18:
            return 'Under 18'
        elif age <= 25:
            return '18-25'
        elif age <= 35:
            return '26-35'
        elif age <= 45:
            return '36-45'
        elif age <= 55:
            return '46-55'
        elif age <= 65:
            return '56-65'
        else:
            return 'Over 65'

    profiles['user_age_group'] = profiles['age'].apply(age_group)

    # Merge with profiles
    merged = merged.merge(
        profiles[['user_id', 'email', 'user_age_group']],
        on='user_id', how='left'
    )

    # Select and order final columns
    result = merged[['user_id', 'date', 'email', 'user_age_group', 'experiment_name',
                      'supplement_name', 'dosage_grams', 'is_placebo',
                      'average_heart_rate', 'average_glucose', 'sleep_hours', 'activity_level']]

    return result
