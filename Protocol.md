# Measuring Corporate AI Strategy and Adoption

## 1. Theoretical basis

**Research question:** How do firms communicate AI strategy, and how much concrete implementation evidence do their disclosures contain?

Corporate communication can express strategic intent, undertake commitments, or describe action. These statements convey different information: an ambition identifies direction; a commitment identifies an intended action; reported deployment identifies operational activity. Their specificity affects interpretability, but detailed language does not establish implementation or truth.

Following the construct-first approach motivating Majzoubi, Murray, and Mayew (2026), we begin with conceptual distinctions, translate them into observable text criteria, and validate the resulting classifications against human judgments. Our AI categories and scales below are proposed operationalizations, not measures taken from that paper. [Reference paper](https://doi.org/10.1002/smj.70068); [replication materials](https://github.com/Majid-Majzoubi/CEO-promises-SMJ).

This reasoning produces three separate dimensions: **attention** (how much AI is discussed), **intent** (what the firm proposes), and **implementation evidence** (what it reports doing). Investment and governance are supporting dimensions. They should not be combined into one maturity score.

Disclosures are selective, self-reported communication. Mentioning AI is not adoption; silence is not nonadoption. Reported benefits are not independently verified causal effects. The initial study therefore concerns measurement and descriptive comparisons.

## 2. Metrics: what each group measures

| Dimension | Suggested metrics | Definition and interpretation |
|---|---|---|
| Disclosure intensity | `ai_mention_count`; `ai_mentions_per_1000_words` | Nonoverlapping lexical matches; mentions divided by all document words, multiplied by 1,000. Measures attention, including possible false matches. |
| Substantive AI content | `validated_ai_passage_count`; `validated_ai_word_share`; `ai_topic_share` | Human-confirmed AI blocks; their word share; and the narrower share of words in substantive AI claim spans. These distinguish relevant discussion from keyword presence. |
| Strategic orientation | `ai_strategic_priority`; efficiency, innovation, and workforce labels | Explicit firm-specific objectives. Use nonexclusive binary labels; retain intended versus realized actions. |
| Management communication | `ai_commitment_count`; `ai_forward_looking_share`; `ai_specificity_score` | Distinct explicit undertakings; future-oriented statements divided by time-classifiable substantive AI statements; informational detail under the rubric below. |
| Implementation | `adoption_stage`; `reported_deployment`; `adoption_use_case_count` | Evidence stage; presence of current production use; distinct current deployed applications. Separate plans and pilots from deployed cases. |
| Investment and partnerships | `ai_capital_investment`; `ai_partnership` | Explicit AI resource commitments or relationships. Spending and partnership announcements alone do not establish application deployment. |
| Risks and governance | `ai_risk_share`; regulatory, cybersecurity, privacy, governance, and oversight labels | Risk claim words divided by substantive AI claim words; explicit exposures and controls. Risk language remains substantive evidence even when adoption-stage coding is inapplicable. |
| Outcomes | `deployment_scale_reported`; `quantified_outcome`; `outcome_attribution` | Separate users/sites/access counts from realized numerical results explicitly linked to an application. Record metric, period, and baseline when stated. |

For word shares, use the complete document word count as denominator unless otherwise stated. Count overlapping source words once. Validated block share includes surrounding paragraph context; topic share includes only relevant claim spans. Candidate share is neither a validated measure nor true topic share.

**Specificity, proposed 1-5 rubric:** 1 = broad ambition; 2 = named function or activity; 3 = identifiable task and mechanism/action; 4 = level 3 plus an explicit scope, timing, or scale boundary; 5 = level 3 plus at least two independent details, including a measurable criterion with an interpretable scope and reference period/comparator. Specificity is independent of adoption stage: a detailed future plan can score 5 while remaining Stage 2.

## 3. Adoption stages: evidence thresholds

The scale orders the strength of **reported evidence**, not enterprise-wide maturity. Assign the highest stage directly supported for the same application, actor, and time. Higher stages do not require public disclosure of preceding stages.

| Stage | Criterion | Hypothetical example | Main exclusion |
|---|---|---|---|
| 0: No qualifying disclosure | Adequate review finds no substantive strategy/adoption evidence in the defined document and scope | Full-source review finds only generic industry background | An irrelevant passage or keyword absence cannot establish 0 |
| 1: Strategic discussion | Firm-specific AI objective, but no concrete intended application | "AI is central to our customer-experience strategy." | Generic industry optimism |
| 2: Concrete plan | Explicit intended AI use in an identifiable task/function/product | "We plan an AI tool to route service requests." | Possibility without an intended action |
| 3: Pilot | Actual testing or experimental use is reported | "We are piloting the routing tool in two teams." | A planned test; real customers do not automatically imply production |
| 4: Deployment | Current routine operational use or deployed customer-facing product | "The tool routes requests in daily operations." | Marketing capabilities, licenses/access alone, or historical use without continuation evidence |
| 5: Deployment with quantified outcome | Stage 4 plus a realized numerical result explicitly attributed to that application | "The deployed tool reduced handling time from ten to eight minutes." | User counts, projected savings, or unrelated firm revenue growth |
| NA | Evidence insufficient, ambiguous, unreviewed, or stage-ineligible | Deployment status is unclear | Do not replace uncertainty with 0 |

Stage 0 applies to an adequately reviewed document/scope, not individual negative passages. Risk-only statements receive no evidence-level adoption stage. A risk-only document can still receive 0 for its fully reviewed strategy/adoption domain.

Stage 5 adds outcome reporting rather than a distinct operational state. **Recommended convention:** retain the requested 0-5 description, but compare implementation primarily using stages 0-4 (mapping 5 to 4) and independent outcome indicators. A quantified pilot benefit stays Stage 3. An explicit deployed benefit without a baseline can qualify for 5, with the missing baseline recorded; it still does not establish causality or necessarily productivity.

## 4. Parsing and aggregation guidance

**Read -> determine relevance -> identify actor -> separate claims/use cases -> identify scope and time -> assign stage and other attributes -> preserve quotation.**

Classify relevance as `substantive`, `context_only`, `irrelevant`, or `uncertain`. Substantive statements concern the focal firm's strategy, applications, resources, products, risks, or controls; generic industry and competitor discussion is context-only. Product names such as Copilot or Agent require AI context rather than automatic acceptance.

The annotation unit is an independently interpretable evidence statement. Split a paragraph describing multiple applications; combine repeated statements about the same application into one use-case-period record. Keep the original source quotation and location for every decision.

Separate internal operations, customer-facing products, customer-adoption claims, R&D, infrastructure, and partnerships/investment. A vendor selling AI and a customer using AI are different actors and phenomena. Cross-industry comparison should prioritize equivalent scopes.

Record planned, current, historical, discontinued, and unclear status. Resolve apparently conflicting stages by checking dates, units, and applications; do not automatically take the maximum. Repeated annual-report language is repeated disclosure, not necessarily new or continuing implementation.

Aggregate distinct applications, scope-specific deployment presence, and stage distributions. A maximum stage can summarize strongest evidence but does not measure enterprise-wide maturity. Full-document absence and validated shares require adequate source review; partial review supports only explicitly labeled partial results.

## 5. Human evaluation: extraction versus classification

**Extraction asks whether relevant text was retrieved. Classification asks whether its meaning was coded correctly.** These require separate evaluation.

A proposed starting sample is 30 candidates and 30 nonmatching blocks, with 10 of each per firm and representation of different sections. Add difficult examples as a separate diagnostic set. Reviewing candidates alone detects false positives but cannot reveal extraction omissions. Account for the current exact-text deduplication when defining the sampling frame.

Two researchers should independently code relevance, actor/scope, and stage where feasible. Compare original labels, adjudicate disagreements using the written criteria, revise rules on development cases, and freeze them before evaluating a separate holdout. With one coder, inter-coder reliability cannot be estimated.

### 5.1 Extraction confusion matrix

Here the reference label is human substantive relevance; retrieval is the keyword screen.

| Screen result | Human: substantive | Human: not substantive |
|---|---|---|
| Retrieved | True positive (TP) | False positive (FP) |
| Not retrieved | False negative (FN) | True negative (TN) |

- **Precision:** TP / (TP + FP): how much retrieved text is relevant?
- **Recall:** TP / (TP + FN): how much relevant text was retrieved?
- **F1:** 2PR / (P + R): balances precision and recall.
- **Accuracy:** (TP + TN) / all reviewed units; can be misleading when negatives dominate.

Balanced retrieval strata and unequal firm sampling are not representative population samples. Use sampling weights for population estimates or label results sample-specific. A small nonmatching sample with no missed positives does not establish perfect recall. Uncertain human labels and zero denominators must be reported, not converted into correct negatives.

### 5.2 Stage classification confusion matrix

Rows are assigned stages; columns are independently adjudicated reference stages. Each `n_ij` is the number of eligible statements assigned stage i with reference stage j; these are symbols, not results.

| Assigned / reference | 1: Strategy | 2: Plan | 3: Pilot | 4: Deployment | 5: Outcome |
|---|---|---|---|---|---|
| 1 | n_11 | n_12 | n_13 | n_14 | n_15 |
| 2 | n_21 | n_22 | n_23 | n_24 | n_25 |
| 3 | n_31 | n_32 | n_33 | n_34 | n_35 |
| 4 | n_41 | n_42 | n_43 | n_44 | n_45 |
| 5 | n_51 | n_52 | n_53 | n_54 | n_55 |

Diagonal cells are agreement. Cells below the diagonal represent overstatement; above it, understatement. In particular, n_42 and n_43 expose plans/pilots mistaken for deployment. For each stage, precision divides its diagonal count by its row total; recall divides it by its column total. Report class support and abstentions alongside accuracy.

Assess relevance and stage eligibility separately; a wrongly excluded statement must not disappear from error reporting. Stage 0 requires document-level evaluation, and NA is not an ordinal stage. Use raw inter-coder agreement plus Cohen's Kappa for nominal labels and weighted Kappa for eligible ordinal stages; rare classes and small samples limit interpretation.

## 6. Future LLM assistance and research interpretation

LLMs may propose contextual labels and evidence; humans define constructs and provide independent reference judgments. Require exact source-matching quotes, actor/time checks, and review of ambiguous or high-impact assignments. Compare models, instruction variants, and context sizes against the same human-labeled holdout. Model-model agreement is stability, not validity. No automated annotation is undertaken here.

The initial empirical question is whether strategic emphasis accompanies reported implementation. Use a two-dimensional profile or cross-tabulation, not subtraction of word share from ordinal stage. Later questions about firm characteristics or subsequent economic performance require more firms, time periods, and financial data. Selective disclosure, reverse causality, and omitted variables prevent causal interpretation of simple associations.

## 7. Pilot scope and decisions to settle

The current pilot contains three complete 10-Ks and 140 lexical candidates: MSFT 101, WMT 19, JPM 20. Existing word/mention metrics are unvalidated; systematic stage coding and human evaluation remain pending. Partial web extracts are not substitutes for complete sources. Earnings-call speaker and Q&A measures are later extensions.

Before annotation, agree on: the core metric set; adequate review for Stage 0; separate internal/product reporting; the role of Stage 5; the specificity rubric; use-case identity and temporal reconciliation; and feasible double-coding/holdout sizes. The recommended sequence is **agree definitions -> manually test examples -> evaluate extraction and coding -> revise/freeze -> expand annotation -> consider automation and descriptive analysis**.
