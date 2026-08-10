"""
data_quality_checker.py - Modul Deteksi Kualitas Dataset
"""

import pandas as pd
import numpy as np
from scipy import stats
import re

class DataQualityChecker:
    """
    Class untuk mendeteksi masalah pada dataset
    """
    
    def __init__(self):
        self.issues = {}
        self.summary = {}
        self.df = None
        
    def scan_dataset(self, df):
        """
        Scan dataset untuk mendeteksi semua masalah
        """
        self.df = df
        self.issues = {}
        self.summary = {
            'total_rows': len(df),
            'total_cols': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024  # KB
        }
        
        # 1. Cek missing values
        self._check_missing_values()
        
        # 2. Cek tipe data
        self._check_data_types()
        
        # 3. Cek label tidak valid
        self._check_labels()
        
        # 4. Cek kolom kosong
        self._check_empty_columns()
        
        # 5. Cek duplikat
        self._check_duplicates()
        
        # 6. Cek outlier
        self._check_outliers()
        
        # 7. Cek entropi / distribusi data
        self._check_entropy()
        
        # 8. Cek konsistensi data
        self._check_consistency()
        
        # 9. Cek format URL (jika ada)
        self._check_url_format()
        
        # 10. Generate skor kesehatan dataset
        self._generate_health_score()
        
        return self.issues, self.summary
    
    def _check_missing_values(self):
        """Cek missing values per kolom"""
        missing = self.df.isnull().sum()
        missing_pct = (missing / len(self.df)) * 100
        
        self.issues['missing_values'] = {
            'total_missing': missing.sum(),
            'total_missing_pct': (missing.sum() / len(self.df)) * 100,
            'columns': {}
        }
        
        for col in self.df.columns:
            if missing[col] > 0:
                self.issues['missing_values']['columns'][col] = {
                    'count': int(missing[col]),
                    'percentage': round(missing_pct[col], 2)
                }
    
    def _check_data_types(self):
        """Cek tipe data per kolom"""
        self.issues['data_types'] = {
            'numeric_cols': [],
            'categorical_cols': [],
            'mixed_cols': [],
            'issues': []
        }
        
        for col in self.df.columns:
            col_type = str(self.df[col].dtype)
            if 'int' in col_type or 'float' in col_type:
                self.issues['data_types']['numeric_cols'].append(col)
            elif 'object' in col_type:
                # Cek apakah ada campuran tipe data
                unique_types = self.df[col].apply(type).unique()
                if len(unique_types) > 1:
                    self.issues['data_types']['mixed_cols'].append(col)
                    self.issues['data_types']['issues'].append(
                        f"Kolom '{col}' memiliki tipe data campuran: {[t.__name__ for t in unique_types]}"
                    )
                else:
                    self.issues['data_types']['categorical_cols'].append(col)
    
    def _check_labels(self):
        """Cek label tidak valid (untuk klasifikasi)"""
        self.issues['labels'] = {
            'valid_labels': [],
            'invalid_labels': [],
            'missing_label_col': False,
            'issues': []
        }
        
        # Cari kemungkinan label column
        potential_labels = ['label', 'result', 'phishing', 'is_phishing', 'target', 'class', 'Category']
        label_col = None
        
        for col in potential_labels:
            if col in self.df.columns:
                label_col = col
                break
        
        if label_col:
            unique_labels = self.df[label_col].unique()
            valid_labels = [0, 1, '0', '1', 'phishing', 'legitimate', 'safe', 'Phishing', 'Legitimate']
            
            invalid = [str(l) for l in unique_labels if str(l).lower() not in 
                      ['0', '1', 'phishing', 'legitimate', 'legitimate', 'safe', 'nan', 'none']]
            
            if invalid:
                self.issues['labels']['invalid_labels'] = invalid
                self.issues['labels']['issues'].append(
                    f"Label tidak valid ditemukan: {invalid[:5]}..."
                )
            else:
                self.issues['labels']['valid_labels'] = list(unique_labels)
        else:
            self.issues['labels']['missing_label_col'] = True
            self.issues['labels']['issues'].append(
                "Tidak ditemukan kolom label (cari: 'label', 'result', 'phishing', 'target')"
            )
    
    def _check_empty_columns(self):
        """Cek kolom yang semua nilainya kosong"""
        self.issues['empty_columns'] = {
            'empty_cols': [],
            'constant_cols': [],
            'issues': []
        }
        
        for col in self.df.columns:
            # Kolom semua kosong
            if self.df[col].isnull().all():
                self.issues['empty_columns']['empty_cols'].append(col)
                self.issues['empty_columns']['issues'].append(
                    f"Kolom '{col}' semua kosong (100% missing)"
                )
            
            # Kolom dengan nilai konstan
            elif self.df[col].nunique() == 1:
                self.issues['empty_columns']['constant_cols'].append(col)
                self.issues['empty_columns']['issues'].append(
                    f"Kolom '{col}' memiliki nilai konstan ({self.df[col].iloc[0]})"
                )
    
    def _check_duplicates(self):
        """Cek duplikat data"""
        duplicates = self.df.duplicated()
        duplicate_count = duplicates.sum()
        
        self.issues['duplicates'] = {
            'count': int(duplicate_count),
            'percentage': round((duplicate_count / len(self.df)) * 100, 2),
            'issues': []
        }
        
        if duplicate_count > 0:
            self.issues['duplicates']['issues'].append(
                f"Terdapat {duplicate_count} baris duplikat ({self.issues['duplicates']['percentage']}% data)"
            )
    
    def _check_outliers(self):
        """Cek outlier menggunakan IQR method"""
        self.issues['outliers'] = {
            'total_outliers': 0,
            'columns': {},
            'issues': []
        }
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if col != 'label':  # Skip label
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)]
                outlier_count = len(outliers)
                
                if outlier_count > 0:
                    self.issues['outliers']['columns'][col] = {
                        'count': outlier_count,
                        'percentage': round((outlier_count / len(self.df)) * 100, 2),
                        'lower_bound': round(lower_bound, 3),
                        'upper_bound': round(upper_bound, 3)
                    }
                    self.issues['outliers']['total_outliers'] += outlier_count
        
        if self.issues['outliers']['total_outliers'] > 0:
            cols_with_outliers = ', '.join(list(self.issues['outliers']['columns'].keys())[:5])
            self.issues['outliers']['issues'].append(
                f"Outlier terdeteksi di {len(self.issues['outliers']['columns'])} kolom: {cols_with_outliers}"
            )
    
    def _check_entropy(self):
        """Cek entropi distribusi data"""
        self.issues['entropy'] = {
            'columns': {},
            'issues': []
        }
        
        for col in self.df.select_dtypes(include=[np.number]).columns:
            if col != 'label':
                # Cek skewness / kemiringan data
                skewness = self.df[col].skew()
                
                # Cek distribusi
                if abs(skewness) > 2:
                    self.issues['entropy']['columns'][col] = {
                        'skewness': round(skewness, 3),
                        'distribution': 'Highly Skewed' if skewness > 0 else 'Highly Negatively Skewed'
                    }
                    self.issues['entropy']['issues'].append(
                        f"Kolom '{col}' memiliki distribusi yang sangat miring (skewness: {skewness:.3f})"
                    )
        
        # Cek label imbalance
        if 'label' in self.df.columns or any(col in self.df.columns for col in ['label', 'phishing', 'result']):
            label_col = None
            for col in ['label', 'phishing', 'result', 'target']:
                if col in self.df.columns:
                    label_col = col
                    break
            
            if label_col:
                counts = self.df[label_col].value_counts()
                if len(counts) > 1:
                    min_pct = (counts.min() / len(self.df)) * 100
                    max_pct = (counts.max() / len(self.df)) * 100
                    
                    if min_pct < 15:
                        self.issues['entropy']['issues'].append(
                            f"⚠️ Data tidak seimbang! Kelas minoritas hanya {min_pct:.1f}% dari total data"
                        )
    
    def _check_consistency(self):
        """Cek konsistensi data (range values)"""
        self.issues['consistency'] = {
            'issues': []
        }
        
        # Cek nilai negatif untuk kolom yang seharusnya positif
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col not in ['label', 'phishing', 'is_phishing']:
                min_val = self.df[col].min()
                if min_val < 0:
                    self.issues['consistency']['issues'].append(
                        f"⚠️ Kolom '{col}' memiliki nilai negatif ({min_val:.3f}) yang mungkin tidak valid"
                    )
        
        # Cek nilai yang terlalu besar
        for col in numeric_cols:
            if col not in ['label', 'phishing', 'is_phishing']:
                max_val = self.df[col].max()
                if max_val > 1e10:
                    self.issues['consistency']['issues'].append(
                        f"⚠️ Kolom '{col}' memiliki nilai sangat besar ({max_val:.3e})"
                    )
    
    def _check_url_format(self):
        """Cek format URL (jika ada kolom URL)"""
        self.issues['url_format'] = {
            'url_cols': [],
            'invalid_urls': 0,
            'issues': []
        }
        
        url_cols = [col for col in self.df.columns if 'url' in col.lower()]
        
        if url_cols:
            self.issues['url_format']['url_cols'] = url_cols
            
            # Cek validasi URL sederhana
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            invalid_count = 0
            for col in url_cols:
                for url in self.df[col].dropna():
                    if not url_pattern.match(str(url)):
                        invalid_count += 1
                        if invalid_count <= 5:
                            self.issues['url_format']['issues'].append(
                                f"URL tidak valid: {str(url)[:50]}..."
                            )
            
            if invalid_count > 0:
                self.issues['url_format']['invalid_urls'] = invalid_count
                self.issues['url_format']['issues'].append(
                    f"⚠️ Terdapat {invalid_count} URL yang tidak valid"
                )
    
    def _generate_health_score(self):
        """Generate skor kesehatan dataset (0-100)"""
        total_issues = 0
        max_issues = 30  # Maksimum issues yang bisa terdeteksi
        
        # Hitung jumlah issues
        for category, data in self.issues.items():
            if category != 'health_score':
                if isinstance(data, dict) and 'issues' in data:
                    total_issues += len(data['issues'])
                elif isinstance(data, dict):
                    total_issues += 1
        
        # Hitung skor (100 - penalty)
        penalty_per_issue = min(10, 100 / max_issues)
        score = max(0, 100 - (total_issues * penalty_per_issue))
        
        # Tambahan penalty untuk masalah serius
        if self.issues.get('missing_values', {}).get('total_missing', 0) > len(self.df) * 0.1:
            score -= 15
        
        if self.issues.get('duplicates', {}).get('count', 0) > len(self.df) * 0.05:
            score -= 10
        
        if self.issues.get('labels', {}).get('missing_label_col', False):
            score -= 20
        
        self.issues['health_score'] = {
            'score': max(0, min(100, int(score))),
            'level': self._get_health_level(score),
            'total_issues': total_issues
        }
    
    def _get_health_level(self, score):
        """Tentukan level kesehatan dataset"""
        if score >= 90:
            return {'label': 'Sangat Bersih', 'icon': '🌟', 'color': '#00c9a7', 'desc': 'Dataset sangat baik, siap digunakan'}
        elif score >= 75:
            return {'label': 'Bersih', 'icon': '✅', 'color': '#4f7cff', 'desc': 'Dataset baik, beberapa perbaikan kecil'}
        elif score >= 50:
            return {'label': 'Perlu Perbaikan', 'icon': '⚠️', 'color': '#ff9f4a', 'desc': 'Perlu preprocessing sebelum digunakan'}
        else:
            return {'label': 'Kotor', 'icon': '❌', 'color': '#ff6b8a', 'desc': 'Dataset bermasalah, perlu dibersihkan!'}
    
    def get_summary_dataframe(self):
        """Buat summary dalam bentuk dataframe"""
        summary_data = {
            'Kategori': [],
            'Status': [],
            'Detail': []
        }
        
        # 1. Missing Values
        mv = self.issues.get('missing_values', {})
        if mv.get('total_missing', 0) > 0:
            summary_data['Kategori'].append('🧹 Missing Values')
            summary_data['Status'].append(f'⚠️ {mv["total_missing"]} nilai hilang')
            cols = list(mv.get('columns', {}).keys())[:3]
            summary_data['Detail'].append(f'Di kolom: {", ".join(cols)}{"..." if len(cols) > 3 else ""}')
        else:
            summary_data['Kategori'].append('🧹 Missing Values')
            summary_data['Status'].append('✅ Bersih')
            summary_data['Detail'].append('Tidak ada missing values')
        
        # 2. Label
        labels = self.issues.get('labels', {})
        if labels.get('missing_label_col', False):
            summary_data['Kategori'].append('🏷️ Label')
            summary_data['Status'].append('❌ Tidak ada')
            summary_data['Detail'].append('Kolom label tidak ditemukan')
        elif labels.get('invalid_labels'):
            summary_data['Kategori'].append('🏷️ Label')
            summary_data['Status'].append(f'⚠️ {len(labels["invalid_labels"])} tidak valid')
            summary_data['Detail'].append(f'Label: {", ".join(str(l) for l in labels["invalid_labels"][:3])}')
        else:
            summary_data['Kategori'].append('🏷️ Label')
            summary_data['Status'].append('✅ Valid')
            summary_data['Detail'].append(f'Label: {labels.get("valid_labels", [])}')
        
        # 3. Duplikat
        dup = self.issues.get('duplicates', {})
        if dup.get('count', 0) > 0:
            summary_data['Kategori'].append('📋 Duplikat')
            summary_data['Status'].append(f'⚠️ {dup["count"]} baris')
            summary_data['Detail'].append(f'{dup["percentage"]}% data duplikat')
        else:
            summary_data['Kategori'].append('📋 Duplikat')
            summary_data['Status'].append('✅ Bersih')
            summary_data['Detail'].append('Tidak ada duplikat')
        
        # 4. Outlier
        out = self.issues.get('outliers', {})
        if out.get('total_outliers', 0) > 0:
            summary_data['Kategori'].append('📊 Outlier')
            summary_data['Status'].append(f'⚠️ {len(out["columns"])} kolom')
            cols = list(out.get('columns', {}).keys())[:3]
            summary_data['Detail'].append(f'Di kolom: {", ".join(cols)}{"..." if len(cols) > 3 else ""}')
        else:
            summary_data['Kategori'].append('📊 Outlier')
            summary_data['Status'].append('✅ Bersih')
            summary_data['Detail'].append('Tidak ada outlier')
        
        # 5. Entropi/Keseimbangan
        ent = self.issues.get('entropy', {})
        if ent.get('issues'):
            summary_data['Kategori'].append('📈 Distribusi')
            summary_data['Status'].append('⚠️ Perlu perhatian')
            summary_data['Detail'].append(ent['issues'][0][:50] + '...')
        else:
            summary_data['Kategori'].append('📈 Distribusi')
            summary_data['Status'].append('✅ Baik')
            summary_data['Detail'].append('Data terdistribusi dengan baik')
        
        # 6. URL Format
        url = self.issues.get('url_format', {})
        if url.get('invalid_urls', 0) > 0:
            summary_data['Kategori'].append('🔗 URL')
            summary_data['Status'].append(f'⚠️ {url["invalid_urls"]} tidak valid')
            summary_data['Detail'].append('Periksa format URL')
        elif url.get('url_cols'):
            summary_data['Kategori'].append('🔗 URL')
            summary_data['Status'].append('✅ Valid')
            summary_data['Detail'].append(f'{len(url["url_cols"])} kolom URL')
        else:
            summary_data['Kategori'].append('🔗 URL')
            summary_data['Status'].append('ℹ️ Tidak ada')
            summary_data['Detail'].append('Tidak ada kolom URL')
        
        return pd.DataFrame(summary_data)
    
    def get_detailed_report(self):
        """Generate laporan detail HTML"""
        health = self.issues.get('health_score', {})
        score = health.get('score', 0)
        level = health.get('level', {})
        
        report = f"""
        <div style="background: #f8faff; border-radius: 16px; padding: 24px; border: 1px solid #e0e8f5;">
            <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 16px;">
                <div style="font-size: 48px;">{level.get('icon', '📊')}</div>
                <div>
                    <div style="font-size: 28px; font-weight: 800; color: {level.get('color', '#1a2332')};">
                        {score}% - {level.get('label', 'Unknown')}
                    </div>
                    <div style="color: #4a5a7a; font-size: 14px;">{level.get('desc', '')}</div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-top: 16px;">
                <div style="background: white; border-radius: 10px; padding: 12px; text-align: center; border: 1px solid #e0e8f5;">
                    <div style="font-size: 20px; font-weight: 700; color: #1a2332;">{self.summary.get('total_rows', 0)}</div>
                    <div style="font-size: 11px; color: #7a8aa5;">Total Baris</div>
                </div>
                <div style="background: white; border-radius: 10px; padding: 12px; text-align: center; border: 1px solid #e0e8f5;">
                    <div style="font-size: 20px; font-weight: 700; color: #1a2332;">{self.summary.get('total_cols', 0)}</div>
                    <div style="font-size: 11px; color: #7a8aa5;">Total Kolom</div>
                </div>
                <div style="background: white; border-radius: 10px; padding: 12px; text-align: center; border: 1px solid #e0e8f5;">
                    <div style="font-size: 20px; font-weight: 700; color: #1a2332;">{health.get('total_issues', 0)}</div>
                    <div style="font-size: 11px; color: #7a8aa5;">Masalah Ditemukan</div>
                </div>
                <div style="background: white; border-radius: 10px; padding: 12px; text-align: center; border: 1px solid #e0e8f5;">
                    <div style="font-size: 20px; font-weight: 700; color: #1a2332;">{self.summary.get('memory_usage', 0):.1f} KB</div>
                    <div style="font-size: 11px; color: #7a8aa5;">Memory Usage</div>
                </div>
            </div>
        </div>
        """
        return report