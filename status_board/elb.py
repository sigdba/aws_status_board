import yaml
import logging
import boto3

from util import *

ELB = boto3.client("elbv2")

log = logging.getLogger()


def target_health(tg_arn):
    return ELB.describe_target_health(TargetGroupArn=tg_arn)["TargetHealthDescriptions"]


def target_group_health_summary(tg_arn):
    healths = [t["TargetHealth"] for t in target_health(tg_arn)]
    states = {h["State"] for h in healths}
    if states == {"healthy"}:
        return {"is_healthy": True, "is_stable": True, "states": list(states)}

    ret = {
        "states": list(states),
        "reasons": list({h["Reason"] for h in healths if "Reason" in h}),
        "descriptions": list({h["Description"] for h in healths if "Description" in h}),
        "is_stable": False,
    }

    if (
        "healthy" not in states
        or len(states.intersection({"unhealthy", "unused", "unavailable"})) > 0
    ):
        return {**ret, "is_healthy": False}

    return {**ret, "is_healthy": True}


if __name__ == "__main__":
    print(
        yaml.dump(
            target_group_health_summary(
                "arn:aws:elasticloadbalancing:us-east-2:875565619567:targetgroup/ban-p-Targe-BNS1WVNURG9Z/e22f04b26333fe99"
            )
        )
    )
