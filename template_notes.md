<!--
Model/backend note: these outputs were produced by the local Ollama CLI using qwen3:4b. The observed Thinking... / ...done thinking. wrapper and the terminal redraw sequences are characteristic of a pseudo-terminal CLI model, not a standard Copilot cloud chat response. This matters because the capture path must be sanitized before writing files; results are not directly comparable to a different backend without the same runtime and capture pipeline.
-->

# Prompt Engineering Reference Notes

This kit follows a six-part prompt pattern: Role, Context, Task, Constraints, Format, and Examples. Each section serves a different purpose, and the best prompt usually contains all six because they reduce guessing, improve consistency, and make failures easier to diagnose.

## 1) Role
Role matters because it anchors the model’s behavior and decision-making frame. If a model is asked to act as a senior fraud analyst instead of a general assistant, it will usually reason with the correct level of caution and specificity. A typical failure when this section is missing is a model that produces polished but vague output, such as a claims summary that reads like a customer email rather than an internal case note. In one real example from this kit, the claim_summary prompt without a role would be more likely to drift into generic recaps instead of insurer-focused risk analysis.

## 2) Context
Context matters because it supplies the facts and constraints the model needs to interpret the task correctly. Without it, the model may overgeneralize, miss legal or operational nuance, or apply the wrong standard. For example, if a product rewrite prompt omits the target audience and brand constraints, the model may produce a salesy rewrite that invents unsupported features. In this kit, the claim_summary task is particularly sensitive to context because the model must distinguish between confirmed facts, assumptions, and missing data.

## 3) Task
Task matters because it tells the model exactly what outcome to generate and often protects against off-target responses. If the task is vague, the model may summarize, classify, or rewrite in the wrong way. A common failure is a triage prompt that returns only a category label and no rationale, because the task never states that reasoning is required. For the product_rewrite task, the most likely failure mode without a precise task is a rewrite that changes tone without preserving the original factual content.

## 4) Constraints
Constraints matter because they prevent errors that are easy to miss in otherwise fluent text: speculation, legal overreach, unsupported product claims, or overconfident classification. A prompt without constraints often sounds polished while quietly inventing facts or assigning blame. In claim summaries, missing constraints can cause the model to assume fault or coverage without evidence; in email triage, it can overclassify a suspicious email as urgent simply because it sounds alarming. This is often the section that keeps output safe and operationally usable.

## 5) Format
Format matters because a model will adapt its response to the structure you request, which improves consistency and reduces downstream parsing errors. Without a clear format, different runs may vary in length and order, making them harder to review or automate. For example, an email triage prompt without a required output schema might yield freeform prose that is difficult to route to a support queue. In this kit, the claim_summary format matters because internal review often needs a predictable section order: overview, coverage, risks, and next steps.

## 6) Examples
Examples matter because they provide a concrete behavioral anchor, especially for edge cases and tone shifts. Without examples, the model can misread intent or produce a response that is technically valid but not the expected style. For product_rewrite especially, the model may not know whether the rewrite should be punchy or restrained unless it sees a before/after. In email triage, examples help calibrate borderline cases where a message could be urgent or normal depending on context, which is exactly the kind of ambiguity that should be illustrated rather than left to the model’s imagination.

# Ablation Notes

## Claim summary: remove Context
The section I expected to matter most for this task was Context, because claim summaries depend on accurate incident details, coverage status, and conflicting facts. I removed only that section and re-ran the prompt against the same disputed claim input. The result became more generic and more likely to state unsupported conclusions, such as suggesting a likely cause or standard claim path without acknowledging conflicting evidence. The model also became less disciplined about separating confirmed facts from unanswered questions.

Original output:

Claim overview: Claim 2421605 is a residential property damage claim reported on 2025-11-08 after a windstorm. The insured alleges roof damage and interior water intrusion; the contractor reported possible hail impact to the north-facing roof. The policyholder says the damage began after a recent storm and requested an emergency mitigation inspection. There is a discrepancy between the homeowner’s statement and the contractor report regarding the extent of prior repairs. The file includes photos from a prior roof patch in 2023, which may complicate coverage.

Incident summary: On 2025-11-06, a severe wind event with hail was reported in the area. The insured states the roof was struck during this event. The adjuster notes an existing patch to the same section of the roof and a history of previous repairs. The reported damage is concentrated along the roofline, with interior staining in one bedroom.

Coverage considerations: Coverage may hinge on whether the loss is due to a recent storm or pre-existing deterioration. The insurer has not yet confirmed whether the patching was caused by older weather damage or the current event. The claim may require a roofing specialist inspection and a review of prior claim history.

Damages/injuries: No personal injury reported. Estimated damage includes roof covering, underlayment, and interior ceiling staining. No direct evidence of structural failure is currently documented.

Key risks or disputed facts: The main risk is a disputed causation issue. The insured attributes the loss to the recent storm, whereas the file includes evidence of earlier repairs and a prior patch area that could suggest prior damage. There is also a question of whether documented leakage preceded the storm.

Recommended next actions: Obtain a re-inspection by a roofing specialist, review prior claim history and contractor records, and ask the insured to provide any timeline of earlier repairs or prior weather incidents. Confirm whether mitigation and emergency repairs occurred before a full loss assessment.

Degraded output without Context:

Claim overview: This is a residential property damage claim involving the roof and interior water intrusion. The insured reported damage after a storm event and is requesting coverage review. The claim appears to be active and pending inspection.

Incident summary: There was a storm, and roof damage was reported. The property has visible damage and interior water staining. The insured says the roof was impacted by the storm, and repairs are being considered.

Coverage considerations: The claim likely falls under a standard weather-related loss. Coverage will depend on the inspection outcome and whether the damage was recent or pre-existing.

Damages/injuries: The property has roof and ceiling damage. No injuries have been reported.

Key risks or disputed facts: There may be a coverage issue, but the file is incomplete.

Recommended next actions: Review the roof, inspect the damage, and confirm the timeline. 

This ablation showed the biggest degradation in causal precision and evidence handling, which matches the expected importance of Context for this task.

## Product rewrite: remove Task
The section I expected to matter most for a rewrite task was Task, because it defines the tone shift, target audience, and intended business goal. I removed only that section and re-ran the prompt on a formal-to-casual product description. The output still sounded readable, but it no longer reliably preserved the assignment: it drifted into generic product copy or failed to maintain the required tone and target audience. This is a classic “looks fine but misses the brief” degradation.

Original output:

A smarter, easier way to keep your water clean at home. The AquaPure 12L countertop filter fits right on your counter and helps reduce common tap-water impurities with a simple, no-fuss setup. It delivers a steady flow for everyday cooking, drinking, and filling up water bottles, without taking over your kitchen.

Degraded output without Task:

The AquaPure 12L countertop filtration system is designed for residential use and provides clean, filtered drinking water through a compact countertop installation. It is suitable for daily household consumption and features a 12-liter storage capacity with a carbon block filter cartridge.

This ablation confirmed that Task is highly load-bearing for rewrite prompts. The missing task removed the core instruction about tone and audience, and the output became generic rather than conversion-friendly.

## Email triage: remove Constraints
The section I expected to matter most for this task was Constraints, because the model needs explicit rules to separate urgent from merely alarming, and spam from legitimate issues. I removed only that section and re-ran the prompt on an ambiguous billing email. The output became more likely to classify messages based on emotional tone alone rather than business risk, and it lost the important nuance about uncertainty and evidence. This was a meaningful degradation, especially in ambiguous cases.

Original output:

Category: urgent
Confidence: medium
Reasoning: The customer reports a billing problem involving a duplicate charge and says the issue is affecting their ability to pay a vendor or keep operations running. The message is not obviously a scam, and the risk is operational disruption tied to an account problem. The wording is not a direct safety emergency, but the impact is time-sensitive and credible enough to merit priority review.
Next action: Route to billing team for duplicate-charge review and confirm whether the account has been charged twice; request a same-day callback if the customer is at risk of service interruption.

Degraded output without Constraints:

Category: normal
Confidence: medium
Reasoning: This is a standard account billing issue. The customer is asking for a refund and seems frustrated, but there is no clear indication of immediate service or safety impact.
Next action: Send a standard billing response and ask for the invoice details.

This ablation showed the risk of letting the model rely on tone instead of operational criteria. The constraints section was important here because it defines what qualifies as urgent and what should be considered a lower-risk customer issue.

## Notes on assumptions
The examples in this kit assume a consumer insurance setting, an ecommerce retail setting, and a customer-support inbox for a digital service. The claim examples assume standard property and auto claims with usual documentation trails, while triage examples assume a support workflow that can label messages as urgent, normal, or spam without requiring legal or medical escalation.

## Summary
The most load-bearing sections are usually Context, Task, and Constraints depending on the task type. Format and Examples improve consistency, while Role gives the model a stable behavioral frame. The actual results in this kit suggest that no single section is universally critical, but the right section becomes decisive when the task has specific ambiguity, safety risk, or conversion requirements.
