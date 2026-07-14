import ReactMarkdown from "react-markdown";

import { getArchetypeTheme } from "../data/archetypes";
import { ProfileScale } from "./ProfileScale";

const CONFIDENCE_LABELS = {
    high: "Точность анализа: высокая",
    medium: "Точность анализа: достаточная",
    low: "Для точности нужно больше деталей",
};

function ReportBrand({ onRestart }) {
    return (
        <button className="report-brand" onClick={onRestart} type="button" aria-label="Вернуться к началу анкеты">
            <span className="report-dots" aria-hidden="true"><i /><i /><i /><i /></span>
            <div>
                <div className="report-logo">MBTI</div>
                <div className="report-subtitle">Личный профиль</div>
            </div>
        </button>
    );
}

export function ProfileReport({ result, onRestart, accentStyle }) {
    const theme = getArchetypeTheme(result.mbti_type);
    const themeStyle = {
        "--type-accent": theme.color,
        "--type-accent-soft": theme.softColor,
    };

    return (
        <div className="results report-enter" style={{ ...themeStyle, ...accentStyle }}>
            <aside className="report-sidebar">
                <ReportBrand onRestart={onRestart} />
                <div className="report-status">
                    <span aria-hidden="true">✦</span>
                    <div>
                        <strong>Профиль готов</strong>
                        <small>Ваш индивидуальный результат</small>
                    </div>
                </div>
                <p className="report-disclaimer">
                    Анализ носит исследовательский и ознакомительный характер и не заменяет профессиональную психологическую диагностику.
                </p>
                <button className="restart-btn" onClick={onRestart} type="button">
                    Пройти ещё раз <span aria-hidden="true">→</span>
                </button>
            </aside>

            <main className="report-content">
                <div className="report-container">
                    <div className="result-kicker">
                        <span>Ваш результат</span>
                        <div className="result-meta">
                            <span className="type-family">{theme.title}</span>
                            <span className={`confidence-badge ${result.confidence || "low"}`}>
                                {CONFIDENCE_LABELS[result.confidence] || CONFIDENCE_LABELS.low}
                            </span>
                        </div>
                    </div>

                    <div className="result-type">{result.mbti_type}</div>

                    <section className="analytics-section" aria-label="Шкалы профиля">
                        <ProfileScale left="Интроверсия" right="Экстраверсия" percent={result.percent.E} color={theme.color} />
                        <ProfileScale left="Сенсорика" right="Интуиция" percent={result.percent.N} color={theme.color} />
                        <ProfileScale
                            left="Этика"
                            right="Логика"
                            percent={result.percent.T}
                            color={theme.color}
                        />
                        <ProfileScale left="Иррациональность" right="Рациональность" percent={result.percent.J} color={theme.color} />
                    </section>

                    <div className="ai-portrait-header">
                        <span className="portrait-eyebrow">Интерпретация</span>
                        <p>Портрет строится по Вашим ответам и описывает вероятные предпочтения, а не диагноз или ограничение.</p>
                    </div>

                    <article className="portrait-section">
                        <ReactMarkdown>{result.portrait}</ReactMarkdown>
                    </article>

                    <div className="print-button-wrapper">
                        <button className="download-btn" onClick={() => window.print()} type="button">
                            Сохранить как PDF
                        </button>
                    </div>
                </div>
            </main>
        </div>
    );
}
