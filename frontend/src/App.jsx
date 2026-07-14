import { useEffect, useState } from "react";

import { ProfileReport } from "./components/ProfileReport";
import { QuestionPanel } from "./components/QuestionPanel";
import { QuestionSidebar } from "./components/QuestionSidebar";
import { useQuestionnaire } from "./hooks/useQuestionnaire";
import "./styles.css";

const ACCENT_THEMES = [
    { id: "purple", color: "#7d6be9", soft: "#eeebff", contrast: "#ffffff" },
    { id: "yellow", color: "#efad39", soft: "#fff5de", contrast: "#352400" },
    { id: "pink", color: "#b71691", soft: "#fbe9f6", contrast: "#ffffff" },
    { id: "green", color: "#799a4a", soft: "#eff4e7", contrast: "#ffffff" },
];

function getNextAccent(previousId) {
    const candidates = ACCENT_THEMES.filter(({ id }) => id !== previousId);
    return candidates[Math.floor(Math.random() * candidates.length)];
}

function getInitialAccent() {
    const previousId = window.sessionStorage.getItem("mbti-accent");
    const accent = getNextAccent(previousId);
    window.sessionStorage.setItem("mbti-accent", accent.id);
    return accent;
}

export default function App() {
    const questionnaire = useQuestionnaire();
    const [accent, setAccent] = useState(getInitialAccent);
    const accentStyle = {
        "--ui-accent": accent.color,
        "--ui-accent-soft": accent.soft,
        "--ui-accent-contrast": accent.contrast,
    };

    const restart = () => {
        const nextAccent = getNextAccent(accent.id);
        window.sessionStorage.setItem("mbti-accent", nextAccent.id);
        setAccent(nextAccent);
        questionnaire.restart();
    };

    useEffect(() => {
        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }, [questionnaire.currentQuestion, questionnaire.result]);

    if (questionnaire.result) {
        return <ProfileReport result={questionnaire.result} onRestart={restart} accentStyle={accentStyle} />;
    }

    return (
        <div className="layout" style={accentStyle}>
            <QuestionSidebar
                answers={questionnaire.answers}
                currentQuestion={questionnaire.currentQuestion}
                onSelect={questionnaire.setCurrentQuestion}
            />
            <QuestionPanel
                answer={questionnaire.answers[questionnaire.currentQuestion]}
                answerStats={questionnaire.answerStats}
                canContinue={questionnaire.canContinue}
                currentQuestion={questionnaire.currentQuestion}
                currentStats={questionnaire.currentStats}
                error={questionnaire.error}
                isLast={questionnaire.isLast}
                loading={questionnaire.loading}
                onBack={questionnaire.goBack}
                onChange={questionnaire.updateCurrentAnswer}
                onNext={questionnaire.advance}
            />
        </div>
    );
}
