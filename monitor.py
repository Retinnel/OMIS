import psutil
import time
import random
from database import get_session, Metric, Algorithm

class MetricCollector:
    def __init__(self):
        self.session = get_session()

    def collect_system_metrics(self):
        """Сбор реальных метрик хоста"""
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        
        # Симулируем задержку ответа системы (latency)
        # Если CPU высокий, задержка растет (аномалия)
        base_latency = 50 # мс
        latency = base_latency + (cpu * 2) + random.uniform(-10, 10)
        
        metric = Metric(
            cpu_usage=cpu,
            ram_usage=ram,
            request_latency=latency,
            source="System_Main"
        )
        self.session.add(metric)
        self.session.commit()
        return metric

class AlgorithmSimulator:
    """Класс для симуляции работы алгоритмов (Сценарий A/B тестирования)"""
    
    @staticmethod
    def run_algorithm(algo_type):
        """
        Симулирует выполнение алгоритма.
        algo_type 'v1.0' - медленнее, но меньше памяти.
        algo_type 'v2.0' - быстрее, но больше памяти.
        """
        start_time = time.time()
        
        if algo_type == 'Sort v1.0':
            # Симуляция: Сортировка пузырьком (медленно)
            time.sleep(random.uniform(0.1, 0.3)) 
            mem_impact = 10
        elif algo_type == 'Sort v2.0':
             # Симуляция: Быстрая сортировка (быстро)
            time.sleep(random.uniform(0.05, 0.1))
            mem_impact = 30
        
        duration = (time.time() - start_time) * 1000 # мс
        return duration, mem_impact