# Lab 3-1: Prometheus 쿼리 모음

## 📋 개요

이 문서는 MLOps 모니터링에 자주 사용되는 PromQL 쿼리를 정리한 것입니다.

## 🔧 기본 쿼리

### 1. 시스템 메트릭

#### CPU 사용량

```promql
# Pod CPU 사용량 (5분 평균)
sum(rate(container_cpu_usage_seconds_total{namespace="kubeflow-userXX"}[5m])) by (pod)

# 네임스페이스 전체 CPU 사용량
sum(rate(container_cpu_usage_seconds_total{namespace="kubeflow-userXX"}[5m]))

# CPU 사용률 (%)
sum(rate(container_cpu_usage_seconds_total{namespace="kubeflow-userXX"}[5m])) by (pod) 
/ 
sum(container_spec_cpu_quota{namespace="kubeflow-userXX"} / container_spec_cpu_period{namespace="kubeflow-userXX"}) by (pod) 
* 100
```

#### Memory 사용량

```promql
# Pod Memory 사용량 (bytes)
sum(container_memory_usage_bytes{namespace="kubeflow-userXX"}) by (pod)

# Memory 사용량 (MiB)
sum(container_memory_usage_bytes{namespace="kubeflow-userXX"}) by (pod) / 1024 / 1024

# Memory 사용률 (%)
sum(container_memory_usage_bytes{namespace="kubeflow-userXX"}) by (pod) 
/ 
sum(container_spec_memory_limit_bytes{namespace="kubeflow-userXX"}) by (pod) 
* 100
```

#### Network I/O

```promql
# 네트워크 수신 (bytes/s)
sum(rate(container_network_receive_bytes_total{namespace="kubeflow-userXX"}[5m])) by (pod)

# 네트워크 송신 (bytes/s)
sum(rate(container_network_transmit_bytes_total{namespace="kubeflow-userXX"}[5m])) by (pod)
```

---

## 📊 KServe / 모델 서빙 메트릭

### 2. 요청 관련 메트릭

```promql
# 요청 수 (RPS - Requests Per Second)
rate(revision_request_count{namespace="kubeflow-userXX"}[1m])

# 총 요청 수
sum(increase(revision_request_count{namespace="kubeflow-userXX"}[1h]))

# 서비스별 요청 수
sum(rate(revision_request_count{namespace="kubeflow-userXX"}[5m])) by (service_name)
```

### 3. 지연 시간 (Latency)

```promql
# 평균 응답 시간 (초)
rate(revision_request_latencies_sum{namespace="kubeflow-userXX"}[5m]) 
/ 
rate(revision_request_latencies_count{namespace="kubeflow-userXX"}[5m])

# P95 응답 시간
histogram_quantile(0.95, sum(rate(revision_request_latencies_bucket{namespace="kubeflow-userXX"}[5m])) by (le, service_name))

# P99 응답 시간
histogram_quantile(0.99, sum(rate(revision_request_latencies_bucket{namespace="kubeflow-userXX"}[5m])) by (le, service_name))

# P50 응답 시간 (중앙값)
histogram_quantile(0.50, sum(rate(revision_request_latencies_bucket{namespace="kubeflow-userXX"}[5m])) by (le))
```

### 4. 에러율

```promql
# HTTP 5xx 에러율 (%)
sum(rate(revision_request_count{namespace="kubeflow-userXX", response_code_class="5xx"}[5m])) 
/ 
sum(rate(revision_request_count{namespace="kubeflow-userXX"}[5m])) 
* 100

# HTTP 4xx 에러율 (%)
sum(rate(revision_request_count{namespace="kubeflow-userXX", response_code_class="4xx"}[5m])) 
/ 
sum(rate(revision_request_count{namespace="kubeflow-userXX"}[5m])) 
* 100

# 성공률 (%)
sum(rate(revision_request_count{namespace="kubeflow-userXX", response_code_class="2xx"}[5m])) 
/ 
sum(rate(revision_request_count{namespace="kubeflow-userXX"}[5m])) 
* 100
```

---

## 🎯 InferenceService 전용 메트릭

### 5. KServe 메트릭

```promql
# InferenceService 요청 수
sum(rate(kserve_inference_request_total{namespace="kubeflow-userXX"}[5m])) by (model_name)

# 추론 지연 시간
histogram_quantile(0.95, sum(rate(kserve_inference_request_duration_seconds_bucket{namespace="kubeflow-userXX"}[5m])) by (le, model_name))

# 모델별 에러 수
sum(increase(kserve_inference_request_total{namespace="kubeflow-userXX", status="error"}[1h])) by (model_name)
```

---

## 🔔 알림용 쿼리

### 6. 알림 조건

```promql
# 높은 에러율 (> 5%)
sum(rate(revision_request_count{namespace="kubeflow-userXX", response_code_class="5xx"}[5m])) 
/ 
sum(rate(revision_request_count{namespace="kubeflow-userXX"}[5m])) 
> 0.05

# 높은 지연 시간 (P95 > 500ms)
histogram_quantile(0.95, sum(rate(revision_request_latencies_bucket{namespace="kubeflow-userXX"}[5m])) by (le)) 
> 0.5

# Pod 재시작 (1시간 내)
increase(kube_pod_container_status_restarts_total{namespace="kubeflow-userXX"}[1h]) > 3

# Pod Down
kube_pod_status_phase{namespace="kubeflow-userXX", phase="Running"} == 0
```

---

## 📈 대시보드용 쿼리

### 7. 종합 메트릭

```promql
# 실행 중인 Pod 수
count(kube_pod_status_phase{namespace="kubeflow-userXX", phase="Running"})

# Ready InferenceService 수
count(kube_customresource_inferenceservice_status{namespace="kubeflow-userXX", status="Ready"})

# 총 CPU 요청량
sum(kube_pod_container_resource_requests{namespace="kubeflow-userXX", resource="cpu"})

# 총 Memory 요청량 (GiB)
sum(kube_pod_container_resource_requests{namespace="kubeflow-userXX", resource="memory"}) / 1024 / 1024 / 1024
```

---

## 💡 사용 팁

### Grafana에서 변수 사용

대시보드에서 네임스페이스를 변수로 설정하면 쿼리를 재사용할 수 있습니다:

```promql
# 변수 정의
label_values(kube_namespace_labels, namespace)

# 쿼리에서 변수 사용
sum(rate(container_cpu_usage_seconds_total{namespace="$namespace"}[5m])) by (pod)
```

### 시간 범위 선택

- **실시간 모니터링**: `[1m]` ~ `[5m]`
- **트렌드 분석**: `[1h]` ~ `[24h]`
- **용량 계획**: `[7d]` ~ `[30d]`

---

## 📚 참고 자료

- [PromQL 공식 문서](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Prometheus 함수 레퍼런스](https://prometheus.io/docs/prometheus/latest/querying/functions/)
- [KServe 메트릭 문서](https://kserve.github.io/website/latest/modelserving/observability/prometheus/)
