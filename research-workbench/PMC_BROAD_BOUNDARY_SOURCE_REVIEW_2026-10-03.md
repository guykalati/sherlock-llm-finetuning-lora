# Broad cardiovascular boundary source review — 2026-10-03

## Scope and provenance

This is a purposive re-review of 12 previously used development articles under [the chosen broader cardiovascular policy](PMC_BROAD_SCOPE_POLICY_2026-10-03.md). It is neither independent validation nor retroactive regrading of historical evaluations. The freeze describes deliberate selection using earlier metadata or label strata to expose difficult boundaries; those earlier article labels and model outputs were not consulted. The sample cannot estimate full-corpus accuracy, prevalence or generalization.

The supplied frozen packets were reviewed using the research skill against primary-source contents: each abstract and every extracted narrative paragraph of kind `p`, including embedded captions or table text when present in those paragraphs. Separate tables, figures and supplements were not independently reviewed. Packet byte hashes and the policy byte hash match the boundary freeze. The XML SHA values below are copied from the frozen source provenance; XML was not downloaded or independently rehashed. Citations resolve to the exact recorded PMC XML version. Paragraph indices and section arrays are retained exactly from the packets.

## Findings and boundaries

There are six clinical and six preclinical or mechanistic articles, with no review articles in this purposive set. Three have a primary cardiovascular topic and four a substantive secondary topic. Four are background-only and one remains unresolved. These counts describe only the selected development cases.

The main broad-relevance failures are healthy-diet rationale without a cardiovascular analysis, enzyme engineering justified by hyperuricemia associations, diabetes biomarker work that did not assess cardiovascular complications, and renal all-cause survival interpreted through cardiovascular literature. Existing disease risk, cardiovascular words, blood pressure covariates, or an all-cause death endpoint do not by themselves supply the missing cardiovascular question. Conversely, the psoriasis study directly analyzes cardiovascular risk components, the myasthenia study directly compares cardiovascular/cerebrovascular comorbidity, and the lupus study measures cardiovascular screening processes. Their cardiovascular content is therefore substantive under the policy.

Experimental tier must follow the methods. Human endothelial cultures, human cell lines, secondary human myocardial molecular datasets and citations to patient phenotypes do not convert mechanistic animal or cellular experiments into original clinical outcomes research. Cardiac-cell infection endpoints remain distinguishable from organ function. The acellular epinephrine study remains unresolved at the topical policy boundary because its specific proposed cardiotoxic mechanism is not directly tested in a cardiac biological system. Its candidate flag is false pending adjudication.

Metadata labels and article tags are discovery hints. They cannot determine a cohort versus case report, review versus original experiment, cardiovascular relevance, or evidence tier. No metadata-derived tier is used here. In this set all clinical records describe cohort or survey observations rather than single-case reports; all experimental records retain their animal, cellular or acellular population. This is a single-agent draft, not expert gold. Rationale reflects the complete narrative; the two short quotations per article locate supporting design and topic evidence and cannot independently prove absence of an analysis.

Every article remains unadmitted. A positive topic candidate is only a draft topical decision. Licensing, notices/retraction, source identity, usable body, benchmark overlap, deduplication, partition and other admission checks remain separate gates. No models were called, historical records changed, or training started.

## Exact-version sources and review coverage

| Primary source | Evidence group | Topical role | Narrative paragraphs read |
|---|---|---|---:|
| [PMC9738010 version XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC9738010.1/PMC9738010.1.xml) | clinical | background_only | 20 |
| [PMC5074518 version XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC5074518.1/PMC5074518.1.xml) | preclinical | background_only | 25 |
| [PMC4730864 version XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC4730864.1/PMC4730864.1.xml) | clinical | background_only | 21 |
| [PMC13500855 version XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC13500855.1/PMC13500855.1.xml) | preclinical | primary | 37 |
| [PMC5460254 version XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC5460254.1/PMC5460254.1.xml) | preclinical | primary | 29 |
| [PMC8096277 version XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC8096277.1/PMC8096277.1.xml) | preclinical | primary | 45 |
| [PMC9394444 version XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC9394444.1/PMC9394444.1.xml) | preclinical | secondary_substantive | 40 |
| [PMC11353756 version XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC11353756.1/PMC11353756.1.xml) | clinical | secondary_substantive | 49 |
| [PMC11834866 version XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC11834866.1/PMC11834866.1.xml) | clinical | secondary_substantive | 22 |
| [PMC5824886 version XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC5824886.1/PMC5824886.1.xml) | preclinical | unresolved | 22 |
| [PMC9214991 version XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC9214991.1/PMC9214991.1.xml) | clinical | secondary_substantive | 23 |
| [PMC12656480 version XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC12656480.1/PMC12656480.1.xml) | clinical | background_only | 27 |

## Structured draft decisions

```json
[
  {
    "pmcid": "PMC9738010",
    "xml_sha256": "038279b15dc8d2fd59485662ee305eeb711cf797d0f93cbbbf3449c30a20f9ab",
    "evidence_group": "clinical",
    "subtype": "Population cross-sectional diabetes and renal biomarker study",
    "topical_role": "background_only",
    "topic_candidate": false,
    "rationale": "The analyses relate adiponectin and albuminuria to prevalent type 2 diabetes. Blood pressure and lipids are covariates; prior cardiovascular associations provide context. The study expressly did not assess cardiovascular complications, so these risk-related measurements do not establish a cardiovascular study question.",
    "uncertainty": [
      "Abstract and methods report different participant counts (1751 versus 1771).",
      "Cross-sectional associations cannot establish future diabetes or cardiovascular prediction; medication information is incomplete."
    ],
    "review_extent": "full extracted narrative paragraphs; separate tables/figures/supplements not independently reviewed",
    "training_admission": false,
    "reference_quality": "single-agent draft source review; not expert gold",
    "evidence": [
      {
        "supports": "design",
        "paragraph_index": 12,
        "section": [
          "5. Discussion"
        ],
        "quote": "We performed a cross-sectional study"
      },
      {
        "supports": "topic",
        "paragraph_index": 18,
        "section": [
          "5. Discussion"
        ],
        "quote": "we did not assess the status of the participants"
      }
    ]
  },
  {
    "pmcid": "PMC5074518",
    "xml_sha256": "a6851f215d6546ab376db5e16f8105e10bd698484f8d34ca04b8e496cf460429",
    "evidence_group": "preclinical",
    "subtype": "Acellular yeast-enzyme structural and biochemical engineering; food application",
    "topical_role": "background_only",
    "topic_candidate": false,
    "rationale": "Recombinant yeast purine nucleoside phosphorylase variants are characterized structurally and biochemically and tested on beer. Hyperuricemia and cardiovascular associations motivate the application, but cardiovascular physiology, disease, prevention effects, or risk links are not directly tested. This broad mechanistic group does not imply cardiovascular preclinical evidence.",
    "uncertainty": [
      "The preclinical designation uses the policy broad mechanistic category for purified-protein experiments; this is food enzyme engineering rather than a disease model.",
      "No organismal purine, hyperuricemia or cardiovascular outcome is measured."
    ],
    "review_extent": "full extracted narrative paragraphs; separate tables/figures/supplements not independently reviewed",
    "training_admission": false,
    "reference_quality": "single-agent draft source review; not expert gold",
    "evidence": [
      {
        "supports": "design",
        "paragraph_index": 3,
        "section": [
          "Introduction"
        ],
        "quote": "we report the structural and biochemical characterization"
      },
      {
        "supports": "topic",
        "paragraph_index": 36,
        "section": [
          "Discussion"
        ],
        "quote": "lowering the purine content in a beer sample"
      }
    ]
  },
  {
    "pmcid": "PMC4730864",
    "xml_sha256": "7ae811d35d6089d057faad6caa33a23a249edf0cccea1f13f23dd207703b2689",
    "evidence_group": "clinical",
    "subtype": "Cross-sectional school survey of youth dietary behavior",
    "topical_role": "background_only",
    "topic_candidate": false,
    "rationale": "The study estimates fruit and vegetable consumption and its demographic, school and spending predictors. Cardiovascular protection motivates dietary guidance, but cardiovascular outcomes, physiology or direct cardiovascular risk links are not analyzed. General healthy eating alone does not satisfy substantive cardiovascular prevention research.",
    "uncertainty": [
      "Self-reported dietary frequency is not a cardiovascular risk measurement.",
      "A broader nutrition corpus could include this article, but that would extend the chosen cardiovascular question."
    ],
    "review_extent": "full extracted narrative paragraphs; separate tables/figures/supplements not independently reviewed",
    "training_admission": false,
    "reference_quality": "single-agent draft source review; not expert gold",
    "evidence": [
      {
        "supports": "design",
        "paragraph_index": 4,
        "section": [
          "METHODS",
          "Procedure"
        ],
        "quote": "nationally generalizable school-based, paper-and-pencil survey"
      },
      {
        "supports": "topic",
        "paragraph_index": 3,
        "section": [],
        "quote": "examine FV consumption and predictors of meeting FV recommendations"
      }
    ]
  },
  {
    "pmcid": "PMC13500855",
    "xml_sha256": "8a4c77e0829fb6a87b56b9073f25882d9e8da0646bf203e9030148b7fce37ef3",
    "evidence_group": "preclinical",
    "subtype": "Mouse endothelial conditional knockdown and myocardial infarction; human coronary endothelial cell culture; secondary human myocardial molecular datasets",
    "topical_role": "primary",
    "topic_candidate": true,
    "rationale": "The central question is endothelial ADAM17 and cardiac repair after induced myocardial infarction. Mouse survival, rupture and ventricular dysfunction are direct cardiac outcomes. Cell experiments include human coronary endothelial cells and mouse fibroblasts; public human myocardial single-nucleus datasets provide molecular comparison. These human components do not create an original human clinical outcomes cohort.",
    "uncertainty": [
      "Animal sex differences limit generalization.",
      "Purchased human cells and secondary human molecular data are mechanistic evidence; human clinical effectiveness is untested."
    ],
    "review_extent": "full extracted narrative paragraphs; separate tables/figures/supplements not independently reviewed",
    "training_admission": false,
    "reference_quality": "single-agent draft source review; not expert gold",
    "evidence": [
      {
        "supports": "design",
        "paragraph_index": 7,
        "section": [
          "Methods",
          "Myocardial infarction surgery and functional analysis"
        ],
        "quote": "Myocardial infarction was induced by permanent ligation"
      },
      {
        "supports": "topic",
        "paragraph_index": 16,
        "section": [
          "Results",
          "Loss of endothelial ADAM17 compromises survival and exacerbates cardiac dysfunction Post-MI"
        ],
        "quote": "LV dilation and systolic dysfunction"
      }
    ]
  },
  {
    "pmcid": "PMC5460254",
    "xml_sha256": "80fe8da96a91fd647aed0a40a4ff7a84b7cb23be8831f796593b4f1c6669490c",
    "evidence_group": "preclinical",
    "subtype": "Transgenic Drosophila myotonic dystrophy repeat models; cardiac and skeletal muscle functional experiments",
    "topical_role": "primary",
    "topic_candidate": true,
    "rationale": "Cardiac dysfunction is a co-primary experimental target alongside skeletal muscle disease. Heart-specific repeat expression is directly assessed for rhythm, systolic and diastolic timing, and fractional shortening. Human patient findings cited in discussion are prior work rather than a newly enrolled clinical cohort.",
    "uncertainty": [
      "Pure repeat fly models do not establish human clinical disease severity or treatment effectiveness.",
      "Skeletal muscle findings and cardiac findings should remain distinguishable."
    ],
    "review_extent": "full extracted narrative paragraphs; separate tables/figures/supplements not independently reviewed",
    "training_admission": false,
    "reference_quality": "single-agent draft source review; not expert gold",
    "evidence": [
      {
        "supports": "design",
        "paragraph_index": 14,
        "section": [
          "Materials and Methods",
          "Drosophila strains"
        ],
        "quote": "Transgenic flies were generated by injecting the plasmids"
      },
      {
        "supports": "topic",
        "paragraph_index": 11,
        "section": [
          "Results",
          "Heart dysfunction in both DM1 and DM2 model flies includes systolic and diastolic alterations, arrhythmia, and contractility defects"
        ],
        "quote": "Heart contraction, measured as a percentage of fractional shortening"
      }
    ]
  },
  {
    "pmcid": "PMC8096277",
    "xml_sha256": "d826dfed5858b5afabe5c71232c687e2f2c4c17012b82136b28e802411b57ca5",
    "evidence_group": "preclinical",
    "subtype": "CRISPR zebrafish Mto1 knockout cardiomyopathy model; human HEK293T molecular experiments",
    "topical_role": "primary",
    "topic_candidate": true,
    "rationale": "The experiments directly study cardiac development and adult hypertrophic cardiomyopathy in zebrafish, including myocardial hypertrophy, disarray and mitochondrial mechanisms. Human HEK293T experiments concern protein interactions; references to patient phenotypes do not establish new clinical outcome observations.",
    "uncertainty": [
      "Animal phenotype resemblance does not demonstrate clinical validity in humans.",
      "Human cell-line experiments remain mechanistic; no newly studied patient cohort is described."
    ],
    "review_extent": "full extracted narrative paragraphs; separate tables/figures/supplements not independently reviewed",
    "training_admission": false,
    "reference_quality": "single-agent draft source review; not expert gold",
    "evidence": [
      {
        "supports": "design",
        "paragraph_index": 25,
        "section": [
          "RESULTS",
          "Generation of  mto1  knock-out zebrafish using CRISPR/Cas9 system"
        ],
        "quote": "we used the CRISPR/Cas9 technology to generate zebrafish mutant"
      },
      {
        "supports": "topic",
        "paragraph_index": 27,
        "section": [
          "RESULTS",
          "The  mto1  mutants exhibited hypertrophic cardiomyopathy in adult zebrafish."
        ],
        "quote": "hypertrophy of cardiac myocytes and myocardial fiber disarray"
      }
    ]
  },
  {
    "pmcid": "PMC9394444",
    "xml_sha256": "251c646398248fb11d7f0dc4dd3aa5cd4ca27e38ec2fafd7d41d610a72f6c166",
    "evidence_group": "preclinical",
    "subtype": "Trypanosoma cruzi infection experiments in murine macrophages, rat cardiac-derived H9C2 myoblasts and mouse marrow-derived cells",
    "topical_role": "secondary_substantive",
    "topic_candidate": true,
    "rationale": "The main question is ursolic acid-mediated host-cell xenophagy and parasite reduction. Cardiac-derived H9C2 cells are directly infected and assayed alongside macrophages, making the cardiac infection component substantive. The study measures intracellular infection and cell viability, not cardiac contractility or clinical Chagas cardiomyopathy.",
    "uncertainty": [
      "H9C2 rat myoblasts are a surrogate rather than mature human cardiac tissue.",
      "The therapeutic and cardiomyopathy implications exceed the demonstrated cellular endpoints; cited prior in vivo efficacy is not a new clinical experiment."
    ],
    "review_extent": "full extracted narrative paragraphs; separate tables/figures/supplements not independently reviewed",
    "training_admission": false,
    "reference_quality": "single-agent draft source review; not expert gold",
    "evidence": [
      {
        "supports": "design",
        "paragraph_index": 5,
        "section": [
          "Methods",
          "Cell Culture"
        ],
        "quote": "RAW 264.7 (murine macrophages) and H9C2 (rat myoblast) cells"
      },
      {
        "supports": "topic",
        "paragraph_index": 37,
        "section": [
          "Discussion"
        ],
        "quote": "in cardiac cells, without affecting host cell viability"
      }
    ]
  },
  {
    "pmcid": "PMC11353756",
    "xml_sha256": "94a4cdaded6b9bca34b3bf8d85892cb4e8da9ba90acfc0fe6583051a352b2dc3",
    "evidence_group": "clinical",
    "subtype": "Retrospective cross-sectional psoriasis and metabolic syndrome comparison",
    "topical_role": "secondary_substantive",
    "topic_candidate": true,
    "rationale": "The psoriasis-centered study directly compares hypertension, lipid and other metabolic syndrome components and relates measured metabolic variables to psoriasis severity. These analyzed cardiovascular risk components satisfy the policy explicit metabolic syndrome boundary. Cardiovascular event incidence and prevention effectiveness are not demonstrated.",
    "uncertainty": [
      "Groups are defined partly by metabolic components, so group contrasts should not be read as causal effects of psoriasis.",
      "The described multiplicity threshold and some post-hoc significance interpretations appear inconsistent."
    ],
    "review_extent": "full extracted narrative paragraphs; separate tables/figures/supplements not independently reviewed",
    "training_admission": false,
    "reference_quality": "single-agent draft source review; not expert gold",
    "evidence": [
      {
        "supports": "design",
        "paragraph_index": 7,
        "section": [
          "2. Materials and Methods",
          "2.1. Patient Selection"
        ],
        "quote": "This retrospective cross-sectional study was conducted"
      },
      {
        "supports": "topic",
        "paragraph_index": 13,
        "section": [
          "3. Results",
          "3.1. PSO–MS and PSO Group Analysis"
        ],
        "quote": "AHT presence was also statistically significantly different"
      }
    ]
  },
  {
    "pmcid": "PMC11834866",
    "xml_sha256": "87e5476df47e28b97fdee554f3b61a82cb167090bb695468be3a2ae8eb1f732a",
    "evidence_group": "clinical",
    "subtype": "Retrospective cross-sectional myasthenia gravis clinical records; clustering and autoantibody associations",
    "topical_role": "secondary_substantive",
    "topic_candidate": true,
    "rationale": "Cardiovascular and cerebrovascular comorbidity is directly compared across myasthenia subtypes and analyzed in antibody-associated clinical patterns. It is more than a baseline mention. The central disease remains myasthenia gravis and these are existing composite comorbidities, not prospective cardiovascular events.",
    "uncertainty": [
      "The source alternates between 644 and 664 patients.",
      "Cross-sectional prevalence comparisons do not establish incidence, prospective prediction or causation; age and composite disease definitions constrain interpretation."
    ],
    "review_extent": "full extracted narrative paragraphs; separate tables/figures/supplements not independently reviewed",
    "training_admission": false,
    "reference_quality": "single-agent draft source review; not expert gold",
    "evidence": [
      {
        "supports": "design",
        "paragraph_index": 4,
        "section": [
          "Materials and methods",
          "Data collection"
        ],
        "quote": "This was a cross-sectional retrospective study"
      },
      {
        "supports": "topic",
        "paragraph_index": 17,
        "section": [
          "Results",
          "Differences among MGFA subtypes"
        ],
        "quote": "coexisting cardiovascular and cerebrovascular diseases"
      }
    ]
  },
  {
    "pmcid": "PMC5824886",
    "xml_sha256": "0206dc9cae887dd73dc4984b745470d9cabc7c10aa506f23b7e4e584801fe514",
    "evidence_group": "preclinical",
    "subtype": "Acellular epinephrine-iron coordination and redox experiments with proposed cardiovascular mechanism",
    "topical_role": "unresolved",
    "topic_candidate": false,
    "rationale": "Purified chemical-solution experiments characterize epinephrine-iron reactions and oxidant generation at physiological pH. The discussion explicitly proposes a cardiotoxic mechanism, but no cardiac cells, tissues, injury or cardiovascular physiology are assayed. The mechanism is more specific than an incidental disease mention, yet the policy does not clearly settle admission of acellular chemistry justified by proposed cardiotoxicity.",
    "uncertainty": [
      "Policy adjudication is needed for acellular proposed cardiovascular mechanisms without direct cardiac biological measurements.",
      "Concentration relevance and translation to cardiac injury remain hypotheses; biomaterials are another proposed application."
    ],
    "review_extent": "full extracted narrative paragraphs; separate tables/figures/supplements not independently reviewed",
    "training_admission": false,
    "reference_quality": "single-agent draft source review; not expert gold",
    "evidence": [
      {
        "supports": "design",
        "paragraph_index": 13,
        "section": [
          "Methods",
          "Chemicals"
        ],
        "quote": "All experiments were performed using bidistilled deionized ultrapure"
      },
      {
        "supports": "topic",
        "paragraph_index": 11,
        "section": [
          "Discussion"
        ],
        "quote": "represents a plausible chemical mechanism of the cardiotoxic effects"
      }
    ]
  },
  {
    "pmcid": "PMC9214991",
    "xml_sha256": "e1cc70da6827ad8ee4c8550523fd51cb2b3fa3b18c87206ce613255fac4f4031",
    "evidence_group": "clinical",
    "subtype": "Cross-sectional lupus health-services quality-indicator comparison across clinics",
    "topical_role": "secondary_substantive",
    "topic_candidate": true,
    "rationale": "The study directly compares documented cardiovascular risk factor assessment across clinic settings and provides adjusted estimates. This is substantive cardiovascular prevention-process research within a wider lupus care evaluation. It does not measure resulting cardiovascular events or prove that improved documentation improves patient outcomes.",
    "uncertainty": [
      "Documentation and self-report influence measured care performance.",
      "Clinic selection and care processes may confound comparisons; patient outcome effects were not assessed."
    ],
    "review_extent": "full extracted narrative paragraphs; separate tables/figures/supplements not independently reviewed",
    "training_admission": false,
    "reference_quality": "single-agent draft source review; not expert gold",
    "evidence": [
      {
        "supports": "design",
        "paragraph_index": 4,
        "section": [
          "Methods",
          "Study design and participants"
        ],
        "quote": "In this cross-sectional study, we recruited patients in 2016"
      },
      {
        "supports": "topic",
        "paragraph_index": 13,
        "section": [
          "Results"
        ],
        "quote": "cardiovascular risk factor assessment"
      }
    ]
  },
  {
    "pmcid": "PMC12656480",
    "xml_sha256": "0bc8e4fa850d932fbc2d5f56ecdb45cde3abcb8eb38fe3a36f0e19c9e62be5f3",
    "evidence_group": "clinical",
    "subtype": "Prospective maintenance-hemodialysis cohort; adipokine association with all-cause mortality",
    "topical_role": "background_only",
    "topic_candidate": false,
    "rationale": "The cohort tests leptin, adiponectin and their ratio against all-cause survival and nutritional or inflammatory correlates. Cardiovascular literature and possible mechanisms motivate interpretation, but cause-specific cardiovascular mortality was unavailable. Diabetes, vascular access and laboratory covariates do not turn renal all-cause survival into a directly analyzed cardiovascular outcome.",
    "uncertainty": [
      "The source explicitly lacks cause-specific mortality including cardiovascular death.",
      "Prior cardiovascular findings and proposed cardioprotective mechanisms do not establish a substantive cardiovascular analysis in this cohort.",
      "Observational residual confounding, single biomarker measurements and missing covariates limit causal interpretation."
    ],
    "review_extent": "full extracted narrative paragraphs; separate tables/figures/supplements not independently reviewed",
    "training_admission": false,
    "reference_quality": "single-agent draft source review; not expert gold",
    "evidence": [
      {
        "supports": "design",
        "paragraph_index": 19,
        "section": [
          "4. Materials and Methods",
          "4.1. Study Population"
        ],
        "quote": "The MADRAD study is a prospective cohort study"
      },
      {
        "supports": "topic",
        "paragraph_index": 17,
        "section": [
          "3. Discussion"
        ],
        "quote": "we lacked information on cause-specific mortality"
      }
    ]
  }
]
```
