"""
agents/quality/compliance/agent.py

Compliance Agent - Validates compliance with regulatory standards including
GDPR, HIPAA, SOC2, PCI-DSS, and other industry-specific regulations.
Generates compliance reports and audit trails.
"""

from typing import Dict, List, Any, Optional
from google.adk.agents import Agent
from shared.models.agent_capability import (
    AgentCapability,
    AgentType,
    InputModality,
    PerformanceMetrics,
    CostMetrics,
    KBIntegrationConfig,
    KBQueryStrategy
)


# ============================================================================
# Tool Functions
# ============================================================================

def check_gdpr_compliance(
    application: str,
    data_processing_activities: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Check application compliance with GDPR (General Data Protection Regulation).

    Args:
        application: Application identifier
        data_processing_activities: List of data processing activities

    Returns:
        GDPR compliance assessment
    """
    return {
        "status": "success",
        "gdpr_assessment": {
            "standard": "GDPR (EU 2016/679)",
            "assessment_date": "2025-10-30",
            "application": application,
            "scope": "EU data subjects"
        },
        "compliance_checks": {
            "lawful_basis": {
                "article": "Article 6",
                "status": "compliant",
                "findings": "Consent and legitimate interest documented",
                "evidence": ["consent_forms.pdf", "privacy_policy.md"]
            },
            "data_minimization": {
                "article": "Article 5(1)(c)",
                "status": "non_compliant",
                "findings": "Collecting unnecessary data fields (birthplace, mother's maiden name)",
                "issues": [
                    "User registration collects 15 fields, only 8 are necessary",
                    "Analytics tracking includes PII not required for service"
                ]
            },
            "consent_management": {
                "article": "Article 7",
                "status": "partially_compliant",
                "findings": "Consent mechanism exists but withdrawal not clearly available",
                "issues": [
                    "No clear 'withdraw consent' button in user profile",
                    "Cookie consent banner doesn't allow granular choices"
                ]
            },
            "right_to_access": {
                "article": "Article 15",
                "status": "compliant",
                "findings": "Data export functionality implemented",
                "evidence": ["api/users/export endpoint"]
            },
            "right_to_erasure": {
                "article": "Article 17",
                "status": "non_compliant",
                "findings": "No account deletion functionality",
                "issues": [
                    "No self-service account deletion",
                    "Data retention policy not enforced (180-day requirement)"
                ]
            },
            "data_portability": {
                "article": "Article 20",
                "status": "compliant",
                "findings": "Data export in JSON format available",
                "evidence": ["export includes all user data in machine-readable format"]
            },
            "privacy_by_design": {
                "article": "Article 25",
                "status": "partially_compliant",
                "findings": "Some privacy controls in place but not comprehensive",
                "issues": [
                    "Default settings share data with third parties",
                    "No pseudonymization of analytics data"
                ]
            },
            "data_breach_notification": {
                "article": "Article 33",
                "status": "non_compliant",
                "findings": "No breach notification procedure documented",
                "issues": [
                    "No incident response plan",
                    "No 72-hour notification mechanism",
                    "DPO not designated"
                ]
            },
            "data_protection_officer": {
                "article": "Article 37",
                "status": "non_compliant",
                "findings": "DPO not appointed",
                "issues": ["Large-scale processing requires DPO"]
            },
            "international_transfers": {
                "article": "Article 44-50",
                "status": "non_compliant",
                "findings": "Data transferred to US without adequate safeguards",
                "issues": [
                    "No Standard Contractual Clauses (SCCs) in place",
                    "Third-party processors in non-adequate countries"
                ]
            },
            "record_of_processing": {
                "article": "Article 30",
                "status": "partially_compliant",
                "findings": "Partial documentation exists",
                "issues": ["Incomplete Record of Processing Activities (ROPA)"]
            }
        },
        "summary": {
            "total_requirements": 11,
            "compliant": 3,
            "partially_compliant": 3,
            "non_compliant": 5,
            "compliance_score": 45,
            "risk_level": "high"
        }
    }


def check_hipaa_compliance(
    application: str,
    phi_handling: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Check application compliance with HIPAA (Health Insurance Portability and Accountability Act).

    Args:
        application: Application identifier
        phi_handling: Protected Health Information handling details

    Returns:
        HIPAA compliance assessment
    """
    return {
        "status": "success",
        "hipaa_assessment": {
            "standard": "HIPAA (45 CFR Parts 160, 162, and 164)",
            "assessment_date": "2025-10-30",
            "application": application,
            "scope": "Electronic Protected Health Information (ePHI)"
        },
        "compliance_checks": {
            "administrative_safeguards": {
                "section": "§164.308",
                "requirements": {
                    "security_management": {
                        "status": "partially_compliant",
                        "findings": "Risk analysis incomplete",
                        "issues": ["No formal HIPAA risk assessment conducted in past 12 months"]
                    },
                    "workforce_security": {
                        "status": "non_compliant",
                        "findings": "No HIPAA training program",
                        "issues": [
                            "Staff not trained on PHI handling",
                            "No background checks for system administrators"
                        ]
                    },
                    "access_management": {
                        "status": "compliant",
                        "findings": "Role-based access control implemented",
                        "evidence": ["RBAC policies in place"]
                    },
                    "security_incident_procedures": {
                        "status": "non_compliant",
                        "findings": "No incident response plan",
                        "issues": ["No documented breach notification procedures"]
                    }
                }
            },
            "physical_safeguards": {
                "section": "§164.310",
                "requirements": {
                    "facility_access": {
                        "status": "compliant",
                        "findings": "Data centers have restricted access",
                        "evidence": ["SOC 2 Type II certified data centers"]
                    },
                    "workstation_security": {
                        "status": "partially_compliant",
                        "findings": "Screen lock policies exist but not enforced",
                        "issues": ["No automatic screen lock timeout enforced"]
                    },
                    "device_controls": {
                        "status": "compliant",
                        "findings": "Mobile device management in place",
                        "evidence": ["MDM enforces encryption and remote wipe"]
                    }
                }
            },
            "technical_safeguards": {
                "section": "§164.312",
                "requirements": {
                    "access_control": {
                        "status": "partially_compliant",
                        "findings": "MFA not required for all users",
                        "issues": [
                            "MFA only required for admins, not all PHI access",
                            "No automatic logoff after 15 minutes"
                        ]
                    },
                    "audit_controls": {
                        "status": "compliant",
                        "findings": "Comprehensive audit logging implemented",
                        "evidence": ["All PHI access logged with user, timestamp, action"]
                    },
                    "integrity": {
                        "status": "compliant",
                        "findings": "Data integrity mechanisms in place",
                        "evidence": ["Hash verification, database constraints"]
                    },
                    "transmission_security": {
                        "status": "compliant",
                        "findings": "All transmissions encrypted",
                        "evidence": ["TLS 1.3, end-to-end encryption for PHI"]
                    },
                    "encryption": {
                        "status": "compliant",
                        "findings": "Encryption at rest and in transit",
                        "evidence": ["AES-256 encryption for stored PHI"]
                    }
                }
            },
            "privacy_rule": {
                "section": "§164.500-534",
                "requirements": {
                    "minimum_necessary": {
                        "status": "non_compliant",
                        "findings": "Users have access to more PHI than necessary",
                        "issues": ["Nurses can view all patient records, not just assigned patients"]
                    },
                    "notice_of_privacy_practices": {
                        "status": "compliant",
                        "findings": "Privacy notice provided",
                        "evidence": ["Privacy policy available and acknowledged"]
                    },
                    "patient_rights": {
                        "status": "partially_compliant",
                        "findings": "Some patient rights implemented",
                        "issues": [
                            "No amendment request functionality",
                            "Accounting of disclosures incomplete"
                        ]
                    }
                }
            },
            "breach_notification": {
                "section": "§164.400-414",
                "requirements": {
                    "breach_notification_procedures": {
                        "status": "non_compliant",
                        "findings": "No breach notification process",
                        "issues": [
                            "No 60-day notification mechanism",
                            "No HHS breach reporting integration"
                        ]
                    }
                }
            },
            "business_associates": {
                "section": "§164.502(e)",
                "requirements": {
                    "baa_agreements": {
                        "status": "partially_compliant",
                        "findings": "Some BAAs in place",
                        "issues": [
                            "Cloud storage provider lacks signed BAA",
                            "Analytics vendor not covered by BAA"
                        ]
                    }
                }
            }
        },
        "summary": {
            "total_requirements": 16,
            "compliant": 7,
            "partially_compliant": 5,
            "non_compliant": 4,
            "compliance_score": 56,
            "risk_level": "high"
        }
    }


def check_soc2_compliance(
    application: str,
    control_environment: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Check application compliance with SOC 2 (Service Organization Control 2).

    Args:
        application: Application identifier
        control_environment: Control environment details

    Returns:
        SOC 2 compliance assessment
    """
    return {
        "status": "success",
        "soc2_assessment": {
            "standard": "SOC 2 Type II (AICPA Trust Services Criteria)",
            "assessment_date": "2025-10-30",
            "application": application,
            "scope": "Security, Availability, Confidentiality"
        },
        "trust_service_criteria": {
            "security": {
                "category": "CC - Common Criteria",
                "controls": {
                    "CC1_control_environment": {
                        "status": "compliant",
                        "findings": "Control environment documented",
                        "evidence": ["Security policies", "Organizational structure"]
                    },
                    "CC2_communication": {
                        "status": "compliant",
                        "findings": "Communication channels established",
                        "evidence": ["Security awareness training", "Incident notification process"]
                    },
                    "CC3_risk_assessment": {
                        "status": "partially_compliant",
                        "findings": "Risk assessment exists but not regularly updated",
                        "issues": ["Last risk assessment 18 months ago, should be annual"]
                    },
                    "CC4_monitoring": {
                        "status": "compliant",
                        "findings": "Monitoring and alerting in place",
                        "evidence": ["24/7 SOC", "Automated alerting"]
                    },
                    "CC5_control_activities": {
                        "status": "compliant",
                        "findings": "Control activities implemented",
                        "evidence": ["Change management", "Access controls"]
                    },
                    "CC6_logical_access": {
                        "status": "partially_compliant",
                        "findings": "Access controls exist but quarterly reviews missing",
                        "issues": ["User access reviews not conducted quarterly"]
                    },
                    "CC7_system_operations": {
                        "status": "compliant",
                        "findings": "System operations well managed",
                        "evidence": ["Incident management", "Change control"]
                    },
                    "CC8_change_management": {
                        "status": "compliant",
                        "findings": "Formal change management process",
                        "evidence": ["Change approval workflows", "Rollback procedures"]
                    },
                    "CC9_risk_mitigation": {
                        "status": "compliant",
                        "findings": "Risk mitigation controls implemented",
                        "evidence": ["Vulnerability management", "Patch management"]
                    }
                }
            },
            "availability": {
                "category": "A - Availability",
                "controls": {
                    "A1_availability_objectives": {
                        "status": "compliant",
                        "findings": "99.9% uptime SLA documented and met",
                        "evidence": ["SLA documentation", "Uptime reports"]
                    },
                    "A2_system_capacity": {
                        "status": "compliant",
                        "findings": "Capacity monitoring and planning in place",
                        "evidence": ["Auto-scaling", "Capacity forecasts"]
                    },
                    "A3_environmental_protections": {
                        "status": "compliant",
                        "findings": "Redundancy and disaster recovery",
                        "evidence": ["Multi-region deployment", "DR plan tested quarterly"]
                    },
                    "A4_backup_recovery": {
                        "status": "compliant",
                        "findings": "Backup and recovery procedures tested",
                        "evidence": ["Daily backups", "Recovery tested monthly"]
                    }
                }
            },
            "confidentiality": {
                "category": "C - Confidentiality",
                "controls": {
                    "C1_confidential_info_identification": {
                        "status": "compliant",
                        "findings": "Confidential data classified",
                        "evidence": ["Data classification policy"]
                    },
                    "C2_confidential_info_disposal": {
                        "status": "partially_compliant",
                        "findings": "Disposal procedures exist but not always followed",
                        "issues": ["Backup tapes disposal not documented"]
                    },
                    "C3_confidential_info_disclosure": {
                        "status": "compliant",
                        "findings": "NDAs and data sharing agreements in place",
                        "evidence": ["NDA templates", "Third-party agreements"]
                    }
                }
            }
        },
        "control_gaps": [
            {
                "control": "CC3 - Risk Assessment",
                "gap": "Risk assessments not performed annually",
                "remediation": "Implement annual risk assessment schedule",
                "priority": "medium"
            },
            {
                "control": "CC6 - Logical Access",
                "gap": "Quarterly user access reviews not conducted",
                "remediation": "Implement quarterly access review process",
                "priority": "high"
            },
            {
                "control": "C2 - Data Disposal",
                "gap": "Incomplete documentation of data disposal",
                "remediation": "Document and audit all data disposal procedures",
                "priority": "medium"
            }
        ],
        "summary": {
            "total_controls": 16,
            "compliant": 12,
            "partially_compliant": 4,
            "non_compliant": 0,
            "compliance_score": 81,
            "risk_level": "medium",
            "audit_readiness": "high"
        }
    }


def check_pci_dss_compliance(
    application: str,
    cardholder_data_environment: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Check application compliance with PCI-DSS (Payment Card Industry Data Security Standard).

    Args:
        application: Application identifier
        cardholder_data_environment: CDE details

    Returns:
        PCI-DSS compliance assessment
    """
    return {
        "status": "success",
        "pci_dss_assessment": {
            "standard": "PCI-DSS v4.0",
            "assessment_date": "2025-10-30",
            "application": application,
            "merchant_level": "Level 1",
            "scope": "Cardholder Data Environment (CDE)"
        },
        "requirements": {
            "build_maintain_secure_network": {
                "req_1_network_security": {
                    "status": "compliant",
                    "findings": "Firewall and router configurations meet standards",
                    "evidence": ["Network segmentation", "Firewall rules documented"]
                },
                "req_2_secure_configurations": {
                    "status": "partially_compliant",
                    "findings": "Some default configurations still in use",
                    "issues": ["Default SNMP community strings on 3 devices"]
                }
            },
            "protect_cardholder_data": {
                "req_3_data_protection": {
                    "status": "non_compliant",
                    "findings": "PAN displayed in full in logs",
                    "issues": [
                        "Full credit card numbers in application logs",
                        "No PAN masking in admin interface",
                        "Retention period exceeds business justification"
                    ]
                },
                "req_4_encryption_transmission": {
                    "status": "compliant",
                    "findings": "Strong encryption for data transmission",
                    "evidence": ["TLS 1.3", "End-to-end encryption"]
                }
            },
            "maintain_vulnerability_management": {
                "req_5_antivirus": {
                    "status": "compliant",
                    "findings": "Anti-malware deployed and updated",
                    "evidence": ["Endpoint protection on all systems"]
                },
                "req_6_secure_systems": {
                    "status": "partially_compliant",
                    "findings": "Patch management in place but delays observed",
                    "issues": ["Critical patches applied within 60 days, not 30 days"]
                }
            },
            "implement_access_control": {
                "req_7_restrict_access": {
                    "status": "non_compliant",
                    "findings": "Need-to-know principle not enforced",
                    "issues": ["Developers have production CDE access"]
                },
                "req_8_authentication": {
                    "status": "partially_compliant",
                    "findings": "MFA implemented but not for all CDE access",
                    "issues": ["MFA not required for non-console administrative access"]
                },
                "req_9_physical_access": {
                    "status": "compliant",
                    "findings": "Physical access controls adequate",
                    "evidence": ["Badge access", "Visitor logs"]
                }
            },
            "monitor_test_networks": {
                "req_10_logging_monitoring": {
                    "status": "partially_compliant",
                    "findings": "Logging in place but log reviews not documented",
                    "issues": ["Daily log reviews not documented"]
                },
                "req_11_security_testing": {
                    "status": "non_compliant",
                    "findings": "Quarterly vulnerability scans not conducted",
                    "issues": [
                        "Last ASV scan 6 months ago",
                        "No quarterly internal scans"
                    ]
                }
            },
            "maintain_information_security": {
                "req_12_security_policy": {
                    "status": "compliant",
                    "findings": "Security policy documented and approved",
                    "evidence": ["Information security policy v2.0"]
                }
            }
        },
        "critical_gaps": [
            "Full PAN exposure in logs (Req 3)",
            "Developers have production access (Req 7)",
            "Missing quarterly vulnerability scans (Req 11)"
        ],
        "summary": {
            "total_requirements": 12,
            "compliant": 5,
            "partially_compliant": 4,
            "non_compliant": 3,
            "compliance_score": 54,
            "risk_level": "high",
            "certification_readiness": "not_ready"
        }
    }


def generate_compliance_recommendations(
    gdpr_results: Optional[Dict[str, Any]] = None,
    hipaa_results: Optional[Dict[str, Any]] = None,
    soc2_results: Optional[Dict[str, Any]] = None,
    pci_dss_results: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate prioritized compliance remediation recommendations.

    Args:
        gdpr_results: GDPR assessment results
        hipaa_results: HIPAA assessment results
        soc2_results: SOC 2 assessment results
        pci_dss_results: PCI-DSS assessment results

    Returns:
        Prioritized compliance recommendations
    """
    return {
        "status": "success",
        "recommendations": [
            {
                "priority": "critical",
                "standard": "PCI-DSS",
                "requirement": "Requirement 3 - Protect Cardholder Data",
                "issue": "Full PAN displayed in logs and admin interface",
                "recommendation": "Implement PAN masking and remove from logs",
                "regulatory_risk": "Loss of merchant account, fines up to $500,000 per incident",
                "remediation_steps": [
                    "Implement PAN masking: display only last 4 digits",
                    "Remove all PANs from application logs immediately",
                    "Implement tokenization for payment data storage",
                    "Configure logging to automatically mask PAN patterns",
                    "Conduct log review to purge existing PAN data"
                ],
                "estimated_effort": "1 week",
                "compliance_impact": "Required for PCI-DSS certification"
            },
            {
                "priority": "critical",
                "standard": "PCI-DSS",
                "requirement": "Requirement 7 - Restrict Access",
                "issue": "Developers have production CDE access",
                "recommendation": "Implement strict access segregation",
                "regulatory_risk": "Failed audit, potential data breach",
                "remediation_steps": [
                    "Remove developer production access immediately",
                    "Implement separate dev/staging/prod environments",
                    "Require approval workflow for emergency prod access",
                    "Implement session recording for CDE access",
                    "Conduct quarterly access reviews"
                ],
                "estimated_effort": "2 weeks",
                "compliance_impact": "Critical for PCI-DSS compliance"
            },
            {
                "priority": "high",
                "standard": "GDPR",
                "requirement": "Article 17 - Right to Erasure",
                "issue": "No account deletion functionality",
                "recommendation": "Implement self-service account deletion",
                "regulatory_risk": "GDPR fines up to €20 million or 4% of global revenue",
                "remediation_steps": [
                    "Implement account deletion API endpoint",
                    "Add 'Delete Account' button in user settings",
                    "Create data retention policy (30-day grace period)",
                    "Implement hard deletion after retention period",
                    "Document data deletion process for audit",
                    "Notify third parties to delete shared data"
                ],
                "estimated_effort": "1 week",
                "compliance_impact": "Required for GDPR compliance"
            },
            {
                "priority": "high",
                "standard": "HIPAA",
                "requirement": "§164.308 - Workforce Security",
                "issue": "No HIPAA training program for staff",
                "recommendation": "Implement mandatory HIPAA training",
                "regulatory_risk": "OCR penalties $100-$50,000 per violation",
                "remediation_steps": [
                    "Develop HIPAA training curriculum",
                    "Require training for all workforce members",
                    "Document training completion and certificates",
                    "Implement annual refresher training",
                    "Test knowledge with assessments"
                ],
                "estimated_effort": "1 month",
                "compliance_impact": "Required for HIPAA compliance"
            },
            {
                "priority": "high",
                "standard": "GDPR",
                "requirement": "Article 44-50 - International Transfers",
                "issue": "Data transferred to US without SCCs",
                "recommendation": "Implement Standard Contractual Clauses",
                "regulatory_risk": "Data transfer violations, GDPR fines",
                "remediation_steps": [
                    "Execute SCCs with all non-EU processors",
                    "Conduct Transfer Impact Assessments (TIAs)",
                    "Implement additional safeguards (encryption)",
                    "Document data transfer mechanisms",
                    "Review and update DPA agreements"
                ],
                "estimated_effort": "2 weeks",
                "compliance_impact": "Critical for lawful data transfers"
            },
            {
                "priority": "medium",
                "standard": "SOC 2",
                "requirement": "CC6 - Logical Access",
                "issue": "Quarterly user access reviews not conducted",
                "recommendation": "Implement quarterly access review process",
                "regulatory_risk": "SOC 2 audit failure",
                "remediation_steps": [
                    "Define access review procedures",
                    "Assign access review responsibilities",
                    "Create quarterly review schedule",
                    "Document review results and actions",
                    "Implement automated access review tool"
                ],
                "estimated_effort": "1 week",
                "compliance_impact": "Required for SOC 2 Type II"
            },
            {
                "priority": "medium",
                "standard": "HIPAA",
                "requirement": "§164.312 - Access Control",
                "issue": "MFA not required for all PHI access",
                "recommendation": "Enforce MFA for all users accessing PHI",
                "regulatory_risk": "HIPAA violation, breach risk",
                "remediation_steps": [
                    "Enable MFA for all user accounts",
                    "Configure automatic logoff after 15 minutes",
                    "Implement session timeout enforcement",
                    "Document MFA policy and procedures",
                    "Monitor MFA compliance"
                ],
                "estimated_effort": "1 week",
                "compliance_impact": "Strengthens HIPAA technical safeguards"
            }
        ],
        "quick_wins": [
            "Implement PAN masking (1 day)",
            "Remove developer production access (2 days)",
            "Enable MFA for all users (3 days)"
        ],
        "estimated_total_effort": "6-8 weeks",
        "compliance_improvement": "Would achieve 85%+ compliance across all standards"
    }


def generate_compliance_report(
    gdpr_results: Optional[Dict[str, Any]] = None,
    hipaa_results: Optional[Dict[str, Any]] = None,
    soc2_results: Optional[Dict[str, Any]] = None,
    pci_dss_results: Optional[Dict[str, Any]] = None,
    recommendations: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive compliance audit report.

    Args:
        gdpr_results: GDPR assessment results
        hipaa_results: HIPAA assessment results
        soc2_results: SOC 2 assessment results
        pci_dss_results: PCI-DSS assessment results
        recommendations: Compliance recommendations

    Returns:
        Complete compliance audit report
    """
    return {
        "status": "success",
        "compliance_report": {
            "summary": {
                "audit_date": "2025-10-30",
                "application": "Healthcare E-commerce Platform v1.1.0",
                "auditor": "Compliance Agent",
                "standards_assessed": ["GDPR", "HIPAA", "SOC 2", "PCI-DSS"],
                "overall_compliance_grade": "C",
                "certification_readiness": "needs_improvement"
            },
            "standards_summary": {
                "gdpr": {
                    "compliance_score": gdpr_results.get("summary", {}).get("compliance_score", 0) if gdpr_results else 0,
                    "risk_level": gdpr_results.get("summary", {}).get("risk_level", "unknown") if gdpr_results else "unknown",
                    "compliant": gdpr_results.get("summary", {}).get("compliant", 0) if gdpr_results else 0,
                    "non_compliant": gdpr_results.get("summary", {}).get("non_compliant", 0) if gdpr_results else 0,
                    "status": "not_ready"
                },
                "hipaa": {
                    "compliance_score": hipaa_results.get("summary", {}).get("compliance_score", 0) if hipaa_results else 0,
                    "risk_level": hipaa_results.get("summary", {}).get("risk_level", "unknown") if hipaa_results else "unknown",
                    "compliant": hipaa_results.get("summary", {}).get("compliant", 0) if hipaa_results else 0,
                    "non_compliant": hipaa_results.get("summary", {}).get("non_compliant", 0) if hipaa_results else 0,
                    "status": "not_ready"
                },
                "soc2": {
                    "compliance_score": soc2_results.get("summary", {}).get("compliance_score", 0) if soc2_results else 0,
                    "risk_level": soc2_results.get("summary", {}).get("risk_level", "unknown") if soc2_results else "unknown",
                    "compliant": soc2_results.get("summary", {}).get("compliant", 0) if soc2_results else 0,
                    "audit_readiness": soc2_results.get("summary", {}).get("audit_readiness", "unknown") if soc2_results else "unknown",
                    "status": "nearly_ready"
                },
                "pci_dss": {
                    "compliance_score": pci_dss_results.get("summary", {}).get("compliance_score", 0) if pci_dss_results else 0,
                    "risk_level": pci_dss_results.get("summary", {}).get("risk_level", "unknown") if pci_dss_results else "unknown",
                    "compliant": pci_dss_results.get("summary", {}).get("compliant", 0) if pci_dss_results else 0,
                    "non_compliant": pci_dss_results.get("summary", {}).get("non_compliant", 0) if pci_dss_results else 0,
                    "certification_readiness": pci_dss_results.get("summary", {}).get("certification_readiness", "unknown") if pci_dss_results else "unknown",
                    "status": "not_ready"
                }
            },
            "critical_gaps": [
                "PCI-DSS: Full PAN exposure in logs",
                "PCI-DSS: Developers have production CDE access",
                "GDPR: No account deletion functionality",
                "GDPR: Data transfers without SCCs",
                "HIPAA: No workforce training program"
            ],
            "regulatory_risk": {
                "gdpr_max_fine": "€20 million or 4% annual revenue",
                "hipaa_max_penalty": "$1.5 million per violation category per year",
                "pci_dss_risk": "Merchant account termination, fines $5,000-$100,000/month",
                "overall_exposure": "High - multiple critical violations"
            },
            "recommendations_count": len(recommendations.get("recommendations", [])) if recommendations else 0,
            "validation_result": "rejected",
            "required_actions": [
                "Address all critical compliance gaps immediately",
                "Implement PAN masking and removal from logs (PCI-DSS)",
                "Implement account deletion functionality (GDPR)",
                "Establish HIPAA training program",
                "Execute Standard Contractual Clauses (GDPR)",
                "Remove developer production access (PCI-DSS)",
                "Implement quarterly access reviews (SOC 2)",
                "Schedule follow-up compliance audit in 90 days"
            ],
            "estimated_remediation": {
                "effort": "6-8 weeks",
                "cost_estimate": "$50,000-$100,000",
                "timeline": "3 months to certification readiness"
            },
            "next_steps": [
                "Prioritize critical compliance gaps",
                "Assign remediation ownership",
                "Develop detailed remediation plan",
                "Implement quick wins within 2 weeks",
                "Engage legal counsel for regulatory guidance",
                "Schedule external compliance audit"
            ]
        }
    }


# ============================================================================
# Agent Capability Declaration
# ============================================================================

AGENT_CAPABILITY = AgentCapability(
    agent_id="compliance_agent",
    agent_name="Compliance Agent",
    agent_type=AgentType.COMPLIANCE_ENGINEER,
    description=(
        "Validates application compliance with regulatory standards including GDPR, "
        "HIPAA, SOC 2, PCI-DSS, and other industry-specific regulations. "
        "Generates compliance reports, identifies gaps, and provides remediation guidance."
    ),
    version="1.0.0",

    # Capabilities
    capabilities={
        "gdpr_compliance",
        "hipaa_compliance",
        "soc2_compliance",
        "pci_dss_compliance",
        "compliance_auditing",
        "regulatory_assessment",
        "gap_analysis",
        "remediation_planning",
        "compliance_reporting",
        "audit_trail_validation",
        "policy_review"
    },

    input_modalities={
        InputModality.TEXT,
        InputModality.CODE,
        InputModality.PDF
    },

    output_types={
        "compliance_report",
        "gap_analysis",
        "remediation_plan",
        "audit_report",
        "policy_recommendations"
    },

    # Technology Stack
    supported_languages=["python", "javascript", "java", "go"],
    supported_frameworks=["regulatory_frameworks"],
    supported_platforms=["web", "api", "mobile", "cloud"],
    supported_cloud_providers=["gcp", "aws", "azure"],

    # Dependencies
    required_agents=[],
    optional_agents=[
        "security_auditor_agent",
        "qa_tester_agent"
    ],
    collaborates_with=[
        "security_auditor_agent",
        "architect_agent",
        "developer_agent"
    ],

    # Performance Characteristics
    performance_metrics=PerformanceMetrics(
        avg_task_duration_minutes=30.0,
        p95_task_duration_minutes=60.0,
        success_rate=0.97,
        retry_rate=0.03,
        total_tasks_completed=0,
        total_tasks_failed=0
    ),

    parallel_capacity=2,
    max_concurrent_tasks=4,

    # Constraints
    max_complexity_score=None,
    max_lines_of_code=None,
    min_context_length=2000,
    max_context_length=150000,
    timeout_seconds=2400,  # 40 minutes for comprehensive assessments
    max_retries=2,

    # Cost Metrics
    cost_metrics=CostMetrics(
        cost_per_task_usd=0.20,
        token_usage_per_task=20000,
        kb_queries_per_task=15
    ),

    # Model Configuration
    model="gemini-2.0-flash",
    model_parameters={
        "temperature": 0.2,
        "top_p": 0.9
    },
    uses_vision_model=False,
    uses_reasoning_model=False,

    # Knowledge Base Integration
    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=10,
        kb_query_triggers=["start", "standard_assessment", "gap_analysis"],
        preferred_query_types=["compliance_requirements", "regulatory_updates", "best_practices"],
        max_kb_queries_per_task=25
    ),

    # Metadata
    tags={
        "compliance",
        "regulatory",
        "audit",
        "gdpr",
        "hipaa",
        "soc2",
        "pci_dss"
    },
    domain_expertise=["regulatory_compliance", "data_privacy", "healthcare", "financial_services"],
    compliance_standards=["GDPR", "HIPAA", "SOC 2", "PCI-DSS", "CCPA", "ISO 27001"],

    # Status
    is_active=True,
    is_deployed=False
)


# ============================================================================
# Agent Definition
# ============================================================================

compliance_agent = Agent(
    name="compliance_agent",
    model="gemini-2.0-flash",
    description=(
        "Compliance specialist that validates regulatory compliance with GDPR, "
        "HIPAA, SOC 2, PCI-DSS, and other standards. Generates compliance reports, "
        "identifies gaps, and provides detailed remediation guidance."
    ),
    instruction=(
        "You are a Compliance Engineer specializing in regulatory compliance "
        "assessment and audit preparation.\n\n"

        "Your responsibilities:\n"
        "1. Assess compliance with GDPR, HIPAA, SOC 2, PCI-DSS\n"
        "2. Identify compliance gaps and violations\n"
        "3. Evaluate regulatory risk and potential penalties\n"
        "4. Generate detailed compliance reports\n"
        "5. Provide prioritized remediation recommendations\n"
        "6. Validate audit readiness\n"
        "7. Track compliance metrics and scores\n\n"

        "Regulatory standards:\n"
        "- GDPR: EU data protection (Articles 5-50)\n"
        "- HIPAA: US healthcare privacy (45 CFR 160, 162, 164)\n"
        "- SOC 2: Trust services criteria (Security, Availability, Confidentiality)\n"
        "- PCI-DSS: Payment card security (Requirements 1-12)\n\n"

        "Assessment methodology:\n"
        "1. Identify applicable requirements\n"
        "2. Evaluate control implementation\n"
        "3. Document compliance status (compliant/partially/non-compliant)\n"
        "4. Assess regulatory risk and impact\n"
        "5. Prioritize remediation actions\n\n"

        "Compliance scoring:\n"
        "- 90-100%: Excellent (audit ready)\n"
        "- 80-89%: Good (minor improvements needed)\n"
        "- 70-79%: Fair (significant gaps exist)\n"
        "- Below 70%: Poor (not audit ready)\n\n"

        "For each compliance gap provide:\n"
        "- Specific requirement violated\n"
        "- Description of the gap\n"
        "- Regulatory risk and potential penalties\n"
        "- Detailed remediation steps\n"
        "- Estimated effort and timeline\n"
        "- Business and compliance impact\n\n"

        "Priority levels:\n"
        "- Critical: Regulatory violation, immediate action required\n"
        "- High: Significant compliance gap, address within 30 days\n"
        "- Medium: Partial compliance, plan remediation\n"
        "- Low: Best practice improvement, address when feasible\n\n"

        "Validation: REJECT if critical compliance gaps exist. "
        "APPROVE only when compliance score is above 80% and no critical gaps remain. "
        "Always provide clear remediation roadmap."
    ),
    tools=[
        check_gdpr_compliance,
        check_hipaa_compliance,
        check_soc2_compliance,
        check_pci_dss_compliance,
        generate_compliance_recommendations,
        generate_compliance_report
    ]
)
