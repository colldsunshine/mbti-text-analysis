import { useCallback, useMemo, useState } from "react";

import { analyzeProfile } from "../api/profileApi";
import { QUESTION_COUNT, QUESTIONS } from "../data/questions";

export function answerLength(answer) {
    return answer.replace(/\s+/g, " ").trim().length;
}

function getAnswerStats(answers) {
    const items = QUESTIONS.map((question, index) => {
        const chars = answerLength(answers[index] || "");
        const progress = Math.min(chars / question.minChars, 1);

        return {
            chars,
            progress,
            missing: Math.max(question.minChars - chars, 0),
            complete: progress >= 1,
        };
    });

    const requiredChars = QUESTIONS.reduce((total, question) => total + question.minChars, 0);
    const completedChars = items.reduce(
        (total, item, index) => total + Math.min(item.chars, QUESTIONS[index].minChars),
        0,
    );
    const firstIncomplete = items.findIndex((item) => !item.complete);

    return {
        items,
        overallProgress: Math.round((completedChars / requiredChars) * 100),
        completeCount: items.filter((item) => item.complete).length,
        allComplete: firstIncomplete === -1,
        firstIncomplete,
    };
}

export function useQuestionnaire() {
    const [answers, setAnswers] = useState(() => Array(QUESTION_COUNT).fill(""));
    const [currentQuestion, setCurrentQuestion] = useState(0);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");

    const answerStats = useMemo(() => getAnswerStats(answers), [answers]);
    const currentStats = answerStats.items[currentQuestion];
    const isLast = currentQuestion === QUESTION_COUNT - 1;
    const canContinue = currentStats.complete;
    const canSubmit = answerStats.allComplete;

    const updateCurrentAnswer = useCallback((value) => {
        setAnswers((previousAnswers) => {
            const nextAnswers = [...previousAnswers];
            nextAnswers[currentQuestion] = value;
            return nextAnswers;
        });
    }, [currentQuestion]);

    const goBack = useCallback(() => {
        setError("");
        setCurrentQuestion((index) => Math.max(0, index - 1));
    }, []);

    const restart = useCallback(() => {
        setAnswers(Array(QUESTION_COUNT).fill(""));
        setCurrentQuestion(0);
        setError("");
        setLoading(false);
        setResult(null);
    }, []);

    const advance = useCallback(async () => {
        if (!canContinue) {
            setError(`Добавьте еще ${currentStats.missing} символов.`);
            return;
        }

        if (!isLast) {
            setError("");
            setCurrentQuestion((index) => index + 1);
            return;
        }

        if (!canSubmit) {
            setError("Заполните все вопросы до минимального объема.");
            setCurrentQuestion(answerStats.firstIncomplete);
            return;
        }

        setLoading(true);
        setError("");

        try {
            setResult(await analyzeProfile(answers));
        } catch {
            setError("Не удалось построить портрет. Попробуйте еще раз.");
        } finally {
            setLoading(false);
        }
    }, [answerStats.firstIncomplete, answers, canContinue, canSubmit, currentStats.missing, isLast]);

    return {
        answers,
        answerStats,
        canContinue,
        canSubmit,
        currentQuestion,
        currentStats,
        error,
        goBack,
        isLast,
        loading,
        restart,
        result,
        setCurrentQuestion,
        advance,
        updateCurrentAnswer,
    };
}
