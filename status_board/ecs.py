import yaml
import logging
import boto3

import elb
from util import *

ECS = boto3.client("ecs")

log = logging.getLogger()


def ecs_clusters():
    return pager(ECS, "list_clusters", "clusterArns")


def cluster_arn_to_name(arn):
    return arn.split("/")[-1]


def service_arns(cluster_arn):
    for svc_arn in pager(ECS, "list_services", "serviceArns", cluster=cluster_arn):
        yield svc_arn


def ecs_services(cluster_arn):
    for chunk in chunks(service_arns(cluster_arn), 10):
        res = ECS.describe_services(
            cluster=cluster_arn, services=chunk, include=["TAGS"]
        )
        for svc in res["services"]:
            yield {
                **svc,
                "region": ECS.meta.region_name,
                "cluster_name": cluster_arn_to_name(svc["clusterArn"]),
            }


def service_health_status(svc):
    if svc["status"] != "ACTIVE":
        return {"stability_status": svc["status"], "stability_reason": "service_status"}
    if "taskSets" in svc:
        task_set_status = {t["stabilityStatus"] for t in svc["taskSets"]}
        if len(task_set_status) > 0 and task_set_status != {"STEADY_STATE"}:
            return {
                "stability_status": "UNSTABLE",
                "stability_reason": "task_set_stability",
            }
    if svc["desiredCount"] != svc["runningCount"]:
        return {"stability_status": "UNSTABLE", "stability_reason": "count_mismatch"}
    if svc["pendingCount"] != 0:
        return {"stability_status": "UNSTABLE", "stability_reason": "pending_tasks"}
    if svc["desiredCount"] > 0:
        if "deployments" in svc:
            deployment_states = {d["rolloutState"] for d in svc["deployments"]}
            if len(deployment_states) > 0 and deployment_states != {"COMPLETED"}:
                return {
                    "stability_status": "UNSTABLE",
                    "stability_reason": "deployment_states",
                }
        if "loadBalancers" in svc:
            tg_arns = list({l["targetGroupArn"] for l in svc["loadBalancers"]})
            if len(tg_arns) > 0:
                tg_health = tg_stability = [
                    elb.target_group_health_summary(arn) for arn in tg_arns
                ]
                tg_stability = {h["is_stable"] for h in tg_health}
                if tg_stability != {True}:
                    tg_is_healthy = {h["is_healthy"] for h in tg_health}
                    if tg_is_healthy == {True}:
                        return {
                            "stability_status": "STABILIZING",
                            "stability_reason": "load_balancer_stabilizing",
                        }

                    return {
                        "stability_status": "UNSTABLE",
                        "stability_reason": "load_balancer_unhealthy",
                    }

                    # TODO: Service discovery health check?
                    # TODO: Container health check?
                    # TODO: No tasks draining?

    return {"stability_status": "STEADY_STATE", "stability_reason": ""}


def services_with_health(cluster_arn):
    return [{**s, **service_health_status(s)} for s in ecs_services(cluster_arn)]


def clusters_with_health():
    return [
        {
            "cluster_name": cluster_arn_to_name(arn),
            "services": services_with_health(arn),
        }
        for arn in ecs_clusters()
    ]


if __name__ == "__main__":
    print(yaml.dump(clusters_with_health()))
