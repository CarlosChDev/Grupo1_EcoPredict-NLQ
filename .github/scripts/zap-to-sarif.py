import json
import sys
import hashlib
from pathlib import Path
from html import unescape
import re


def clean_html(text):
    if not text:
        return ""
    text = unescape(text)
    return re.sub(r"<[^>]+>", "", text).strip()


def sarif_level(riskcode):
    return {
        "3": "error",
        "2": "error",
        "1": "warning",
        "0": "note",
    }.get(str(riskcode), "note")


def security_severity(riskcode):
    return {
        "3": "9.0",
        "2": "6.0",
        "1": "3.0",
        "0": "0.0",
    }.get(str(riskcode), "0.0")


def main():
    if len(sys.argv) != 3:
        print("Uso: python zap-to-sarif.py <entrada.json> <salida.sarif>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    with input_file.open("r", encoding="utf-8") as file:
        report = json.load(file)

    alerts = []

    for site in report.get("site", []):
        for alert in site.get("alerts", []):
            alerts.append((site, alert))

    rules = []
    results = []
    registered_rules = set()

    for site, alert in alerts:
        plugin_id = str(alert.get("pluginid", "unknown"))
        alert_ref = str(alert.get("alertRef", plugin_id))
        name = alert.get("name", "OWASP ZAP Alert")

        rule_id = f"ZAP-{alert_ref}"

        if rule_id in registered_rules:
            rule_id = f"ZAP-{plugin_id}-{hashlib.sha1(name.encode()).hexdigest()[:8]}"

        registered_rules.add(rule_id)

        riskcode = str(alert.get("riskcode", "0"))
        riskdesc = alert.get("riskdesc", "Informational")
        confidence = alert.get("confidence", "")
        cwe = alert.get("cweid", "")
        wasc = alert.get("wascid", "")

        description = clean_html(alert.get("desc", ""))
        solution = clean_html(alert.get("solution", ""))

        instances = alert.get("instances", [])

        rules.append({
            "id": rule_id,
            "name": name,
            "shortDescription": {
                "text": name
            },
            "fullDescription": {
                "text": description or name
            },
            "help": {
                "text": solution or "Revisar el hallazgo identificado por OWASP ZAP."
            },
            "properties": {
                "security-severity": security_severity(riskcode),
                "zap-plugin-id": plugin_id,
                "zap-risk": riskdesc,
                "zap-confidence": confidence,
                "cwe": str(cwe),
                "wasc": str(wasc),
                "tags": [
                    "security",
                    "dast",
                    "owasp-zap"
                ]
            }
        })

        instance_count = len(instances)

        if instances:
            first_instance = instances[0]
            uri = first_instance.get("uri", site.get("@name", "unknown"))
            param = first_instance.get("param", "")
            evidence = clean_html(first_instance.get("evidence", ""))

            message = (
                f"{name}. "
                f"Severidad ZAP: {riskdesc}. "
                f"Instancias detectadas: {instance_count}."
            )

            if param:
                message += f" Parámetro: {param}."

            if evidence:
                message += f" Evidencia: {evidence[:300]}."

        else:
            uri = site.get("@name", "unknown")
            message = (
                f"{name}. "
                f"Severidad ZAP: {riskdesc}. "
                f"Instancias detectadas: 0."
            )

        fingerprint_source = f"{rule_id}|{uri}|{instance_count}"
        fingerprint = hashlib.sha256(
            fingerprint_source.encode("utf-8")
        ).hexdigest()

        results.append({
            "ruleId": rule_id,
            "level": sarif_level(riskcode),
            "message": {
                "text": message
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": uri
                        }
                    }
                }
            ],
            "partialFingerprints": {
                "primaryLocationHash": fingerprint
            },
            "properties": {
                "zap-risk": riskdesc,
                "zap-plugin-id": plugin_id,
                "zap-alert-ref": alert_ref,
                "zap-confidence": confidence,
                "zap-instance-count": instance_count,
                "cwe": str(cwe),
                "wasc": str(wasc)
            }
        })

    sarif = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "OWASP ZAP",
                        "version": report.get("@version", "unknown"),
                        "informationUri": "https://www.zaproxy.org/",
                        "rules": rules
                    }
                },
                "results": results
            }
        ]
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(sarif, file, ensure_ascii=False, indent=2)

    print(f"SARIF generado correctamente: {output_file}")
    print(f"Alertas procesadas: {len(alerts)}")
    print(f"Resultados SARIF: {len(results)}")


if __name__ == "__main__":
    main()