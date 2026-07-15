import { memo } from "react";

import { QUESTIONS } from "../data/questions";
import { answerLength } from "../hooks/useQuestionnaire";

function BrandDots() {
    return (
        <span className="brand-dots" aria-hidden="true">
            <i />
            <i />
            <i />
            <i />
        </span>
    );
}

function NavIcon({ index }) {
    const common = { viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "1.8", strokeLinecap: "round", strokeLinejoin: "round", "aria-hidden": true };
    const icons = [
        <svg {...common}><path d="m13.1 2.3-8 11h5.6l-.8 8.4 8-11h-5.6l.8-8.4Z" /></svg>,
        <svg {...common}><path d="M2.5 12s3.4-5.5 9.5-5.5S21.5 12 21.5 12s-3.4 5.5-9.5 5.5S2.5 12 2.5 12Z" /><circle cx="12" cy="12" r="2.5" /></svg>,
        <svg {...common}><path d="M12 3v8M8 7l4 4 4-4M5 15h5v5M19 15h-5v5" /><path d="M3 17.5 5 15l2 2.5M21 17.5 19 15l-2 2.5" /></svg>,
        <svg {...common}><rect x="4.5" y="5.5" width="15" height="15" rx="2" /><path d="M8 3.5v4M16 3.5v4M8 12h8" /></svg>,
        <svg {...common}><path d="M20.7 7.8a5 5 0 0 0-7.1 0L12 9.4l-1.6-1.6a5 5 0 0 0-7.1 7.1L12 23l8.7-8.1a5 5 0 0 0 0-7.1Z" /><path d="M7.7 15.2h2.1l1.4-3.1 2.1 5 1.3-2h2.2" /></svg>,
        <svg {...common}><path d="M20.5 11.4a7.6 7.6 0 0 1-8.1 7.1 8.2 8.2 0 0 1-2.7-.6l-4.2 1.3 1.4-3.7a7.1 7.1 0 0 1-1.2-4 7.6 7.6 0 0 1 8.1-7.1 7.6 7.6 0 0 1 6.7 7Z" /></svg>,
    ];

    return icons[index];
}

export const QuestionSidebar = memo(function QuestionSidebar({
    answers,
    currentQuestion,
    onSelect,
}) {
    return (
        <aside className="sidebar">
            <div className="sidebar-top">
                <BrandDots />
                <div>
                    <div className="logo">MBTI</div>
                    <div className="sidebar-sub">Личный профиль</div>
                </div>
            </div>

            <nav className="questions-nav" aria-label="Вопросы теста">
                {QUESTIONS.map((question, index) => {
                    const progress = Math.min(answerLength(answers[index] || "") / question.minChars, 1);
                    const active = index === currentQuestion;
                    const complete = progress >= 1;

                    return (
                        <button
                            key={question.title}
                            className={`nav-item ${active ? "active-nav" : ""} ${progress > 0 ? "started" : ""} ${complete ? "complete" : ""}`}
                            onClick={() => onSelect(index)}
                            aria-current={active ? "step" : undefined}
                            aria-label={`${index + 1}. ${question.title}${complete ? " — заполнено" : ""}`}
                            type="button"
                        >
                            <span className="nav-left">
                                <span className={`nav-dot ${progress > 0 ? "started" : ""} ${complete ? "filled" : ""}`} />
                                <span className="nav-icon"><NavIcon index={index} /></span>
                                <span>{question.title}</span>
                            </span>
                            <span className="nav-index">{complete ? "✓" : `${Math.round(progress * 100)}%`}</span>
                        </button>
                    );
                })}
            </nav>

            <p className="sidebar-footer">
                Анализ носит исследовательский и ознакомительный характер и не заменяет профессиональную психологическую диагностику.
            </p>
        </aside>
    );
});
