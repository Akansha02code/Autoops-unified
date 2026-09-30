import Link from "next/link";

const stages = ["Intent & classify", "Extract / plan", "Policy check", "Human approval", "Execute"];

export default function Home() {
  return (
    <main className="landing">
      <nav className="landing-nav">
        <Link className="brand" href="/" aria-label="AutoOps home"><span className="brand-mark">A</span> AutoOps</Link>
        <span className="landing-label">MULTI-AGENT OPERATIONS</span>
      </nav>
      <section className="landing-hero">
        <div className="hero-copy">
          <p className="eyebrow">BUSINESS AUTOMATION, IN ONE FLOW</p>
          <h1>Meet your new<br /><span>operations layer.</span></h1>
          <p className="hero-lede">One platform for document-triggered and request-triggered business automation.</p>
          <ul className="value-list">
            <li><span>01</span> One unified processing pipeline</li>
            <li><span>02</span> A shared policy and decision engine</li>
            <li><span>03</span> Human approval where it matters</li>
          </ul>
          <Link className="button button-primary hero-button" href="/dashboard">Enter Dashboard <span aria-hidden="true">↗</span></Link>
        </div>
        <div className="architecture" aria-label="Documents and requests converge into one automated workflow">
          <div className="input-lane">
            <div className="input-node"><span className="node-icon document-icon">▤</span><span><b>Document</b><small>Invoice or PO</small></span></div>
            <div className="input-node request-node"><span className="node-icon request-icon">“</span><span><b>Request</b><small>Natural language</small></span></div>
          </div>
          <div className="flow-join"><span /><span /></div>
          <div className="pipeline-preview">
            <div className="preview-head"><span className="live-dot" /> SHARED AUTOMATION FLOW <span className="preview-live">LIVE</span></div>
            {stages.map((stage, index) => <div className="preview-stage" key={stage}><span className={index < 3 ? "stage-number stage-done" : "stage-number"}>{index < 3 ? "✓" : `0${index + 1}`}</span><span>{stage}</span>{index < stages.length - 1 && <i />}</div>)}
          </div>
          <div className="architecture-caption">Two ways in. One accountable process.</div>
        </div>
      </section>
      <footer className="landing-footer"><span>AutoOps</span><span>Intake <b>→</b> Decisions <b>→</b> Outcomes</span><span>ENGINEERING PROJECT · 2026</span></footer>
    </main>
  );
}
