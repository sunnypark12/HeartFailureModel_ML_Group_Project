import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt

# Load the datasets
df1 = pd.read_csv('./Data/heart_2020_cleaned.csv')
df2 = pd.read_csv('./Data/heart_failure_clinical_records_dataset.csv')
df3 = pd.read_csv('./Data/heart.csv')

# Preprocess the data as before
df1.columns = df1.columns.str.lower().str.replace(' ', '_')
df2.columns = df2.columns.str.lower().str.replace(' ', '_')
df3.columns = df3.columns.str.lower().str.replace(' ', '_')

df1 = df1.rename(columns={'heartdisease': 'target', 'alcoholdrinking': 'alcohol_drinking', 
                          'physicalhealth': 'physical_health', 'mentalhealth': 'mental_health', 
                          'diffwalking': 'diff_walking', 'agecategory': 'age', 
                          'physicalactivity': 'physical_activity', 'genhealth': 'gen_health', 
                          'sleeptime': 'sleep_time', 'kidneydisease': 'kidney_disease', 'skincancer': 'skin_cancer'})

df2 = df2.rename(columns={'death_event': 'target', 'creatinine_phosphokinase': 'creatinine_phosphokinase', 
                          'ejection_fraction': 'ejection_fraction', 'high_blood_pressure': 'high_blood_pressure', 
                          'serum_creatinine': 'serum_creatinine', 'serum_sodium': 'serum_sodium'})

df3 = df3.rename(columns={'heartdisease': 'target', 'chestpaintype': 'chest_pain_type', 'restingbp': 'resting_bp', 
                          'fastingbs': 'fasting_bs', 'restingecg': 'resting_ecg', 'exerciseangina': 'exercise_angina', 
                          'oldpeak': 'oldpeak', 'st_slope': 'st_slope'})

def convert_age(age):
    if '-' in age:
        return int(age.split('-')[0])
    elif '+' in age:
        return int(age.split('+')[0]) + 5
    elif age == '80 or older':
        return 80
    else:
        return int(age)

df1['age'] = df1['age'].apply(convert_age)

# Ensure the 'age' column is present in all datasets
df2['age'] = df2['age']
df3['age'] = df3['age']

if 'smoking' not in df3.columns:
    df3['smoking'] = 'Unknown'

common_cols = ['target', 'age', 'sex', 'smoking']

df1_common = df1[common_cols + ['bmi', 'physical_health', 'mental_health', 'diff_walking', 'physical_activity', 'gen_health', 'sleep_time']]
df2_common = df2[common_cols + ['anaemia', 'creatinine_phosphokinase', 'diabetes', 'ejection_fraction', 'high_blood_pressure', 'platelets', 'serum_creatinine', 'serum_sodium']]
df3_common = df3[common_cols + ['chest_pain_type', 'resting_bp', 'cholesterol', 'fasting_bs', 'resting_ecg', 'maxhr', 'exercise_angina', 'oldpeak', 'st_slope']]

df1_common = df1_common.reindex(columns=common_cols + ['bmi', 'physical_health', 'mental_health', 'diff_walking', 'physical_activity', 'gen_health', 'sleep_time', 'anaemia', 'creatinine_phosphokinase', 'diabetes', 'ejection_fraction', 'high_blood_pressure', 'platelets', 'serum_creatinine', 'serum_sodium', 'chest_pain_type', 'resting_bp', 'cholesterol', 'fasting_bs', 'resting_ecg', 'maxhr', 'exercise_angina', 'oldpeak', 'st_slope'])
df2_common = df2_common.reindex(columns=common_cols + ['bmi', 'physical_health', 'mental_health', 'diff_walking', 'physical_activity', 'gen_health', 'sleep_time', 'anaemia', 'creatinine_phosphokinase', 'diabetes', 'ejection_fraction', 'high_blood_pressure', 'platelets', 'serum_creatinine', 'serum_sodium', 'chest_pain_type', 'resting_bp', 'cholesterol', 'fasting_bs', 'resting_ecg', 'maxhr', 'exercise_angina', 'oldpeak', 'st_slope'])
df3_common = df3_common.reindex(columns=common_cols + ['bmi', 'physical_health', 'mental_health', 'diff_walking', 'physical_activity', 'gen_health', 'sleep_time', 'anaemia', 'creatinine_phosphokinase', 'diabetes', 'ejection_fraction', 'high_blood_pressure', 'platelets', 'serum_creatinine', 'serum_sodium', 'chest_pain_type', 'resting_bp', 'cholesterol', 'fasting_bs', 'resting_ecg', 'maxhr', 'exercise_angina', 'oldpeak', 'st_slope'])

combined_df = pd.concat([df1_common, df2_common, df3_common], ignore_index=True)

categorical_cols = ['sex', 'smoking', 'diff_walking', 'physical_activity', 'gen_health', 'chest_pain_type', 'resting_ecg', 'exercise_angina', 'st_slope']
for col in categorical_cols:
    combined_df[col] = combined_df[col].astype(str).fillna('Unknown')
    le = LabelEncoder()
    combined_df[col] = le.fit_transform(combined_df[col])

combined_df = combined_df.dropna(subset=['target'])

combined_df['target'] = pd.to_numeric(combined_df['target'], errors='coerce')

# Remove rows where target is NaN
combined_df = combined_df.dropna(subset=['target'])

X = combined_df.drop('target', axis=1)
y = combined_df['target']

X = X.apply(pd.to_numeric, errors='coerce')

# Drop columns with only NaN values before imputation
X = X.dropna(axis=1, how='all')

# Fill remaining NaNs with the mean of each column using SimpleImputer
imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X)

# Scale the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_imputed)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Random Forest without PCA
rf = RandomForestClassifier(random_state=42)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
print("Random Forest without PCA")
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Apply PCA
pca = PCA(n_components=6)
X_pca = pca.fit_transform(X_scaled)

# Train-test split for PCA transformed data
X_train_pca, X_test_pca, y_train_pca, y_test_pca = train_test_split(X_pca, y, test_size=0.2, random_state=42)

# Random Forest with PCA
rf_pca = RandomForestClassifier(random_state=42)
rf_pca.fit(X_train_pca, y_train_pca)
y_pred_pca = rf_pca.predict(X_test_pca)
print("\nRandom Forest with PCA")
print("Accuracy:", accuracy_score(y_test_pca, y_pred_pca))
print(classification_report(y_test_pca, y_pred_pca))
