import { QUESTION_COUNT, QUESTIONS } from "../data/questions";
import { ProgressIndicator } from "./ProgressIndicator";

export function QuestionPanel({
    answer,
    answerStats,
    canContinue,
    currentQuestion,
    currentStats,
    error,
    isLast,
    loading,
    onBack,
    onChange,
    onNext,
}) {
    const question = QUESTIONS[currentQuestion];
    const progress = Math.round(currentStats.progress * 100);
    const helperText = currentStats.complete
        ? isLast && !answerStats.allComplete
            ? "Осталось закрыть отмеченные вопросы."
            : "Ответ достаточно подробный."
        : `Еще ${currentStats.missing} символов до устойчивого анализа.`;

    return (
        <main className="content">
            <div className="content-decor" aria-hidden="true">
                <span className="decor-orb decor-orb-one" />
                <span className="decor-orb decor-orb-two" />
                <span className="decor-star">✧</span>
            </div>
            <div className="question-wrapper">
                <header className="assessment-head">
                    <div className="assessment-meta">
                        <span className="question-count">
                            Вопрос {String(currentQuestion + 1).padStart(2, "0")} / {String(QUESTION_COUNT).padStart(2, "0")}
                        </span>
                        <span className="axis-chip">{question.label}</span>
                    </div>
                    <ProgressIndicator
                        completeCount={answerStats.completeCount}
                        progress={answerStats.overallProgress}
                        total={QUESTION_COUNT}
                    />
                </header>

                <section className="question-panel" key={question.title}>
                    <h1 className="question-title">{question.title}</h1>
                    <p className="question-desc">{question.desc}</p>

                    <textarea
                        value={answer}
                        onChange={(event) => onChange(event.target.value)}
                        placeholder="Напишите свободно и на своем языке."
                        minLength={question.minChars}
                        aria-label={question.title}
                    />

                    <div className={`answer-meter ${currentStats.chars > 0 ? "started" : ""}`}>
                        <div className="answer-meter-row">
                            <span>{helperText}</span>
                            <span>{currentStats.chars}/{question.minChars}</span>
                        </div>
                        <div className="answer-meter-track">
                            <div
                                className={`answer-meter-fill ${canContinue ? "complete" : ""}`}
                                style={{ width: `${progress}%` }}
                            />
                        </div>
                    </div>

                    {error && <p className="error" role="alert">{error}</p>}

                    <div className="actions">
                        <button className="ghost-btn" onClick={onBack} disabled={currentQuestion === 0} type="button">
                            <span aria-hidden="true">←</span> Назад
                        </button>
                        <button className="main-btn" onClick={onNext} disabled={loading || (isLast ? !answerStats.allComplete : !canContinue)} type="button">
                            {isLast ? (loading ? "Анализ..." : "Построить портрет") : "Продолжить"} <span aria-hidden="true">→</span>
                        </button>
                    </div>
                </section>
            </div>
        </main>
    );
}
