import streamlit as st
import pandas as pd
import time
import plotly.express as px
from datetime import datetime

# Импорт нашей логики (файлы database.py, monitor.py, analysis.py не меняются)
from database import get_session, Algorithm, Recommendation
from monitor import MetricCollector, AlgorithmSimulator
from analysis import Analyzer

# --- НАСТРОЙКА СТРАНИЦЫ И CSS ---
st.set_page_config(page_title="IS Optimization", layout="wide", initial_sidebar_state="collapsed")

# CSS с исправлением цветов текста и КНОПОК
st.markdown("""
<style>
    /* Основной фон приложения */
    .stApp {
        background-color: #984aff;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* 1. Глобальный текст: заголовки и параграфы черные */
    h1, h2, h3, h4, h5, h6, p {
        color: #0e1117 !important;
    }
    
    /* 2. Карточки (контейнеры): текст внутри них черный */
    .css-card, .css-card div {
        background-color: #c4f5d4;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        color: #0e1117 !important;
    }

    /* 3. ИСПРАВЛЕНИЕ КНОПОК: Текст кнопок всегда белый */
    div.stButton > button p, div.stButton > button div, div.stButton > button {
        color: white !important;
    }
    
    /* Стиль для обычных (второстепенных) кнопок - делаем их темными с белым текстом для контраста */
    div.stButton > button {
        background-color: #2c3e50; /* Темно-синий фон */
        color: white !important;
        border: none;
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
    }
    
    /* Стиль для активной/главной кнопки (Зеленая) */
    .stButton button[kind="primary"] {
        background-color: #4CAF50 !important;
        color: white !important;
        border: none;
    }

    /* 4. Метрики (Цветные квадраты) */
    .metric-box {
        border-radius: 12px;
        padding: 20px;
        color: white !important;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* Текст внутри метрик строго белый */
    .metric-box div, .metric-box .metric-label, .metric-box .metric-value, .metric-box .metric-sub {
        color: white !important;
    }

    .metric-purple { background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%); }
    .metric-blue { background: linear-gradient(135deg, #5b86e5 0%, #36d1dc 100%); }
    .metric-red { background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); }
    
    .metric-value { font-size: 36px; font-weight: bold; margin: 0; }
    .metric-label { font-size: 14px; opacity: 0.9; margin-top: 5px; }
    .metric-sub { font-size: 12px; opacity: 0.7; margin-top: 10px; }

    /* Скрытие стандартного хедера */
    header {visibility: hidden;}
    
    /* Исправление полей ввода (чтобы текст внутри input был виден) */
    .stTextInput input, .stSelectbox div, .stTextArea textarea {
        color: #0e1117 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- ИНИЦИАЛИЗАЦИЯ ---
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'Главная'
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

session = get_session()
collector = MetricCollector()
analyzer = Analyzer()

# --- ФУНКЦИИ ОТРИСОВКИ ---

def render_login():
    """Страница авторизации"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.container():
            # Добавлен color: black
            st.markdown("""
            <div class="css-card" style="text-align: center; padding: 40px; color: black;">
                <h2 style="margin-bottom: 20px; color: black;">Авторизация в системе</h2>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                login = st.text_input("Логин", placeholder="admin")
                password = st.text_input("Пароль", type="password", placeholder="••••••")
                
                submitted = st.form_submit_button("Войти", type="primary", use_container_width=True)
                
                if submitted:
                    if login:
                        st.session_state.page = 'main'
                        if 'dev' in login: st.session_state.user_role = "Разработчик"
                        elif 'arch' in login: st.session_state.user_role = "Архитектор"
                        else: st.session_state.user_role = "Инженер"
                        st.rerun()
                    else:
                        st.error("Введите логин")

def render_navbar():
    """Верхняя навигация"""
    # Обернем текст статуса в div с черным цветом, чтобы было видно
    st.markdown(f"<div style='color: #0e1117; margin-bottom: 10px;'><b>Пользователь:</b> {st.session_state.user_role} | <b>Статус:</b> Online</div>", unsafe_allow_html=True)
    
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 0.5])
    
    with c1:
        if st.button("Главная", type="secondary" if st.session_state.current_tab != 'Главная' else "primary"):
            st.session_state.current_tab = 'Главная'
            st.rerun()
    with c2:
        if st.button("Алгоритмы", type="secondary" if st.session_state.current_tab != 'Алгоритмы' else "primary"):
            st.session_state.current_tab = 'Алгоритмы'
            st.rerun()
    with c3:
        if st.button("Аналитика", type="secondary" if st.session_state.current_tab != 'Аналитика' else "primary"):
            st.session_state.current_tab = 'Аналитика'
            st.rerun()
    with c4:
        if st.button("Рекомендации", type="secondary" if st.session_state.current_tab != 'Рекомендации' else "primary"):
            st.session_state.current_tab = 'Рекомендации'
            st.rerun()
    with c5:
        if st.button("Выйти"):
            st.session_state.page = 'login'
            st.rerun()
    
    st.markdown("---")

def page_dashboard():
    """Главная страница"""
    st.markdown("<h3 style='color: black;'>Мониторинг в реальном времени</h3>", unsafe_allow_html=True)
    
    metric = collector.collect_system_metrics()
    status, rec_text = analyzer.check_anomalies()
    
    c1, c2, c3, c4 = st.columns(4)
    
    # В метриках используем color: white внутри style
    with c1:
        st.markdown(f"""
        <div class="metric-box metric-purple">
            <div class="metric-label" style="color: white;">Загрузка CPU</div>
            <div class="metric-value" style="color: white;">{metric.cpu_usage}%</div>
            <div class="metric-sub" style="color: rgba(255,255,255,0.7);">Сервер: Node-01</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class="metric-box metric-purple">
            <div class="metric-label" style="color: white;">Загрузка GPU</div>
            <div class="metric-value" style="color: white;">{int(metric.cpu_usage * 0.8)}%</div>
            <div class="metric-sub" style="color: rgba(255,255,255,0.7);">Сервер: GPU-01</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-box metric-blue">
            <div class="metric-label" style="color: white;">Память</div>
            <div class="metric-value" style="color: white;">{metric.ram_usage}%</div>
            <div class="metric-sub" style="color: rgba(255,255,255,0.7);">Доступно: -- GB</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        color_class = "metric-red" if metric.request_latency > 100 else "metric-blue"
        st.markdown(f"""
        <div class="metric-box {color_class}">
            <div class="metric-label" style="color: white;">Время выполнения</div>
            <div class="metric-value" style="color: white;">{int(metric.request_latency)}ms</div>
            <div class="metric-sub" style="color: rgba(255,255,255,0.7);">Среднее за 5 мин</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("<h5 style='color: black;'>Динамика нагрузки</h5>", unsafe_allow_html=True)
        
        df = analyzer.get_recent_metrics(30)
        if not df.empty:
            fig = px.area(df, x='timestamp', y=['cpu_usage', 'request_latency'], 
                          color_discrete_sequence=['#6a11cb', '#ff416c'])
            fig.update_layout(
                xaxis_title=None, 
                yaxis_title=None, 
                margin=dict(l=0, r=0, t=0, b=0), 
                height=300,
                paper_bgcolor='rgba(0,0,0,0)', # Прозрачный фон
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='black') # Черный шрифт графика
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ожидание данных...")
        
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Детальный анализ", type="primary"):
        st.session_state.current_tab = 'Аналитика'
        st.rerun()

    time.sleep(2)
    st.rerun()

def page_algorithms():
    """Управление алгоритмами"""
    st.markdown("<h3 style='color: black;'>Управление алгоритмами и A/B Тестирование</h3>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("<h4 style='color: black;'>Активные алгоритмы</h4>", unsafe_allow_html=True)
        
        st.text_input("Алгоритм сортировки v1.0", value="Время выполнения: 45ms | Память: 128MB", disabled=True)
        st.text_input("Алгоритм сортировки v2.0", value="Время выполнения: 32ms | Память: 156MB", disabled=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("<h4 style='color: black;'>A/B тестирование алгоритмов</h4>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            algo_a = st.selectbox("Алгоритм A:", ["Сортировка v1.0", "Поиск v1.0"])
        with c2:
            algo_b = st.selectbox("Алгоритм B:", ["Сортировка v2.0", "Поиск v2.0"])
            
        test_data = st.text_area("Тестовые данные", placeholder="Введите параметры массива или JSON...", height=100)
        
        btn_col, _ = st.columns([1, 4])
        if btn_col.button("Запустить тестирование", type="primary"):
            with st.spinner("Выполнение тестов..."):
                prog_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.02)
                    prog_bar.progress(i + 1)
                
                st.success("Тестирование завершено!")
                
                # ИСПРАВЛЕНИЕ: Добавлен color: #1b5e20 (темно-зеленый) для текста
                st.markdown("""
                <div style="background-color: #e8f5e9; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50; color: #1b5e20;">
                    <strong>Рекомендация системы:</strong><br>
                    Алгоритм B показал на 25% лучшую производительность. Рекомендуется к внедрению.
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def page_analytics():
    """Страница аналитики"""
    st.markdown("<h3 style='color: black;'>Аналитика и отчеты</h3>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.selectbox("Период анализа:", ["Последние 7 дней", "Последние 30 дней", "Сегодня"])
            st.multiselect("Метрики для анализа:", ["Загрузка CPU", "Потребление памяти", "Время выполнения"], default=["Загрузка CPU"])
        
        if st.button("Сформировать отчет", type="primary"):
            st.success("Отчет сформирован")
            
            st.markdown("---")
            st.markdown("<h4 style='color: black;'>Отчет об эффективности инфраструктуры</h4>", unsafe_allow_html=True)
            
            chart_data = pd.DataFrame({
                'Time': range(10),
                'Load': [10, 20, 15, 25, 30, 45, 60, 55, 70, 80]
            })
            st.line_chart(chart_data, x='Time', y='Load')
            
            # ИСПРАВЛЕНИЕ: Добавлен color: #1b5e20
            st.markdown("""
            <div style="background-color: #e8f5e9; padding: 15px; border-radius: 10px; margin-top: 10px; color: #1b5e20;">
                <strong>Прогноз системы:</strong><br>
                Ожидаемый рост нагрузки на 15% в течение следующих 30 дней. Рекомендуется масштабирование кластера.
            </div>
            """, unsafe_allow_html=True)
            
            c_btn1, c_btn2 = st.columns([1, 1])
            c_btn1.button("Изменить параметры")
            c_btn2.button("Экспорт отчета")

        st.markdown('</div>', unsafe_allow_html=True)

def page_recommendations():
    """Страница рекомендаций"""
    st.markdown("<h3 style='color: black;'>Рекомендации системы</h3>", unsafe_allow_html=True)
    
    recs = [
        {
            "title": "Оптимизация алгоритма сортировки",
            "desc": "Высокое потребление памяти. Рекомендуется перейти на версию 2.1",
            "priority": "Высокий",
            "effect": "-20% памяти",
            "color": "#e8f5e9", 
            "border": "#4CAF50",
            "text_color": "#1b5e20" # Темно-зеленый текст
        },
        {
            "title": "Балансировка нагрузки",
            "desc": "Неравномерное распределение запросов между узлами.",
            "priority": "Средний",
            "effect": "+15% производительности",
            "color": "#fff3e0", 
            "border": "#FF9800",
            "text_color": "#e65100" # Темно-оранжевый текст
        }
    ]
    
    for r in recs:
        # ИСПРАВЛЕНИЕ: Используем text_color
        st.markdown(f"""
        <div class="css-card" style="border-left: 5px solid {r['border']}; padding-left: 20px; color: black;">
            <h4 style="margin: 0; color: black;">{r['title']}</h4>
            <p style="margin: 5px 0; color: black;">{r['desc']}</p>
            <div style="background-color: {r['color']}; padding: 5px 10px; border-radius: 5px; display: inline-block; color: {r['text_color']}; margin-top: 10px;">
                <small><strong>Приоритет:</strong> {r['priority']} | <strong>Ожидаемый эффект:</strong> {r['effect']}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Применить: {r['title']}", key=r['title']):
            st.toast(f"Решение '{r['title']}' применяется...", icon="🚀")

# --- РОУТИНГ ---

if st.session_state.page == 'login':
    render_login()
else:
    render_navbar()
    
    if st.session_state.current_tab == 'Главная':
        page_dashboard()
    elif st.session_state.current_tab == 'Алгоритмы':
        page_algorithms()
    elif st.session_state.current_tab == 'Аналитика':
        page_analytics()
    elif st.session_state.current_tab == 'Рекомендации':
        page_recommendations()