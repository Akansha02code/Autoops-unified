"use client";

import { CaseRecord, formatINR } from "../lib/api";
import { StatusBadge } from "./StatusBadge";

const stages = [
  { title: "Document / request trigger", detail: "Intake received" },
  { title: "Intent & classification", detail: "Route the work" },
  { title: "Extraction or planning", detail: "Structure the request" },
  { title: "Policy & business rules", detail: "Evaluate conditions" },
  { title: "Human approval", detail: "Review and decide" },
  { title: "Execution & orchestration", detail: "Carry out the work" },
];

export function PipelineFlow({ record }: { record: CaseRecord | undefined }) {
  const approved = record?.status === "approved";
  const rejected = record?.status === "rejected";
  const activeIndex = !record ? -1 : approved ? 5 : 4;
  return <>
    <div className="pipeline-stage-scroll"><div className="pipeline-flow">{stages.map((stage, index) => {
      let state = !record ? "future" : index < activeIndex ? "done" : index === activeIndex ? "current" : "future";
      if (rejected && index === 4) state = "current rejected";
      if (rejected && index === 5) state = "stopped";
      const marker = state.includes("done") ? "✓" : state.includes("current") ? rejected ? "×" : "●" : state === "stopped" ? "×" : "·";
      return <div className="pipeline-segment" key={stage.title} style={{ display: "contents" }}>
        <article className={`pipeline-step ${state} ${index === 4 && state.includes("current") ? "human" : ""}`}>
          <div className="step-index"><span>STAGE 0{index + 1}</span><span className="step-indicator">{marker}</span></div>
          <h3>{stage.title}</h3><p>{record ? index < activeIndex ? "Completed" : index === activeIndex ? rejected ? "Stopped: rejected" : "Awaiting approval" : "Not reached" : stage.detail}</p>
          {index === 0 && record && <p className="pipeline-note">{record.source_type === "document" ? "▤ Document received" : "“ Request received"}</p>}
          {index === 3 && !!record?.policy_flags?.length && <div className="policy-annotation">{record.policy_flags.map(flag => <span className="flag-pill" key={flag.rule_id} title={flag.action}>{flag.rule_id}</span>)}</div>}
        </article>
        {index < stages.length - 1 && <span className={`step-connector ${record && index < activeIndex ? "done" : ""}`} />}
      </div>;
    })}</div></div>
    {record && <><div className="pipeline-case-summary"><div className="summary-chip"><span>SELECTED CASE</span><b>{record.case_id}</b></div><div className="summary-chip"><span>STATUS</span><StatusBadge status={record.status} /></div><div className="summary-chip"><span>ITEM</span><b>{record.item ?? "Unclassified"}</b></div><div className="summary-chip"><span>VALUE</span><b>{formatINR(record.price)}</b></div></div><p className="pipeline-note">Live case state refreshes every 15 seconds. Completed steps represent processing implied by the case status.</p></>}
    {!record && <p className="pipeline-note">Select a case above to follow its progress through the unified workflow.</p>}
  </>;
}