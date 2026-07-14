const DOT_COLORS = ["#8B78F3", "#F7C054", "#C92CA8", "#BADC6A"];

export function AnalysisLoader() {
    return (
        <div className="analysis-loader" role="status" aria-live="polite">
            <div className="analysis-loader-card">
                <div className="analysis-loader-dots" aria-hidden="true">
                    {DOT_COLORS.map((color, index) => (
                        <span
                            className="analysis-loader-dot"
                            key={color}
                            style={{ backgroundColor: color, animationDelay: `${index * 140}ms` }}
                        />
                    ))}
                </div>
                <p>Собираем Ваш портрет</p>
                <span>Анализируем ответы</span>
            </div>
        </div>
    );
}
