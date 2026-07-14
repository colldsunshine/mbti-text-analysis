export function ProfileScale({ color, left, percent, right }) {
    const isRight = percent >= 50;
    const power = Math.abs(percent - 50) * 2;

    return (
        <div className="scale">
            <div className="scale-head">
                <span>{left}</span>
                <span>{power.toFixed(0)}%</span>
                <span>{right}</span>
            </div>
            <div className="scale-track">
                <div
                    className={`scale-fill ${isRight ? "right" : "left"}`}
                    style={{ width: `${power / 2}%`, background: color }}
                />
            </div>
        </div>
    );
}
