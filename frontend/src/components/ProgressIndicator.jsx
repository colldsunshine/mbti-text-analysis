export function ProgressIndicator({ completeCount, progress, total }) {
    return (
        <div className={`progress-block ${progress > 0 ? "started" : ""}`}>
            <div className="progress-head">
                <span>Заполненность</span>
                <span>{progress}% · {completeCount}/{total}</span>
            </div>
            <div className="progress" aria-label="Общий прогресс заполнения">
                <div className="progress-fill" style={{ width: `${progress}%` }} />
            </div>
        </div>
    );
}
