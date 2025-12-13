import pandas as pd
from database import get_session, Metric, Recommendation

class Analyzer:
    def __init__(self):
        self.session = get_session()

    def get_recent_metrics(self, limit=100):
        query = self.session.query(Metric).filter(Metric.source=="System_Main").order_by(Metric.timestamp.desc()).limit(limit)
        df = pd.read_sql(query.statement, self.session.bind)
        return df.sort_values(by="timestamp")

    def check_anomalies(self):
        """Простая логика выявления аномалий"""
        # Берем последние 10 записей
        df = self.get_recent_metrics(10)
        if df.empty:
            return None

        avg_cpu = df['cpu_usage'].mean()
        avg_latency = df['request_latency'].mean()

        status = "Normal"
        rec = None

        # Пороговые значения (Правила)
        if avg_latency > 150:
            status = "Critical"
            rec = "Обнаружена высокая задержка. Рекомендуется переключение на алгоритм 'Sort v2.0' или масштабирование ресурсов."
        elif avg_cpu > 80:
            status = "Warning"
            rec = "Высокая загрузка CPU. Проверьте фоновые процессы."

        # Если есть рекомендация и она новая, сохраняем в БД
        if rec:
            existing = self.session.query(Recommendation).filter_by(message=rec, status="Pending").first()
            if not existing:
                new_rec = Recommendation(type="Optimization", message=rec, status="Pending")
                self.session.add(new_rec)
                self.session.commit()
        
        return status, rec