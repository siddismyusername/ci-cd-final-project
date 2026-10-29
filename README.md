# ci-cd-final-project

## Project Name

**ci-cd-final-project — Continuous Integration and Delivery with GitHub Actions, Tekton, and OpenShift**

## Project Description

This is the counter-service CI/CD final project for the IBM Continuous Integration and Delivery course. It contains a working Flask REST service, automated Flake8 and Nose checks, a Docker image, and an OpenShift Tekton pipeline.

The public repository and project are both named **ci-cd-final-project**, matching the exact repository-name requirement in the course grading rubric.

## Assignment Submission Links

The following public GitHub files correspond to the source-code assessment criteria:

- **Question 1 — Project name and description:** [README.md](https://github.com/siddismyusername/ci-cd-final-project/blob/main/README.md)
- **Question 2 — Linting with Flake8 and unit tests with Nose:** [.github/workflows/workflow.yml](https://github.com/siddismyusername/ci-cd-final-project/blob/main/.github/workflows/workflow.yml)
- **Question 3 — Tekton cleanup and Nose testing tasks:** [.tekton/tasks.yml](https://github.com/siddismyusername/ci-cd-final-project/blob/main/.tekton/tasks.yml)

The source files are provided for review. Pipeline success must be documented with actual GitHub Actions and OpenShift run output.

## Service API

The service listens on **port 8000** and writes the **SERVICERUNNING** startup message to its logs.

| Method | Path | Operation |
| --- | --- | --- |
| GET | `/` | Service information |
| GET | `/health` | Health check |
| GET | `/counters` | List counters |
| POST | `/counters/{name}` | Create counter |
| GET | `/counters/{name}` | Read counter |
| PUT | `/counters/{name}` | Increment counter |
| DELETE | `/counters/{name}` | Delete counter |

Counters are in memory and do not persist after process restarts. The training deployment uses a single application replica.

## Local Development

Use **Python 3.9** (the version expected by the course's Nose-based lab).

```bash
python3.9 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
flake8 service tests
nosetests -v tests
gunicorn --bind 0.0.0.0:8000 --log-level info service:app
```

```bash
curl -i http://localhost:8000/health
curl -i -X POST http://localhost:8000/counters/sample
curl -i http://localhost:8000/counters/sample
```

## Continuous Integration: GitHub Actions

The workflow at [`.github/workflows/workflow.yml`](.github/workflows/workflow.yml) triggers on pushes to `main`, pull requests, and manual dispatch. It checks out code, configures Python and Node.js, installs dependencies, initializes a container image, lints with Flake8, and runs the Nose unit tests. **A successful workflow must be confirmed from a real GitHub Actions run; the presence of YAML alone does not prove execution.**

## Continuous Delivery: OpenShift Pipelines

The source-controlled Tekton definitions are:

- [`.tekton/tasks.yml`](.tekton/tasks.yml): cleanup, git-clone, Flake8 and Nose Task resources
- [`.tekton/pipeline.yml`](.tekton/pipeline.yml): cleanup → git-clone → flake8 → nose → buildah → deploy (openshift-client)
- [`.tekton/pvc.yml`](.tekton/pvc.yml): PVC `oc-lab-pvc`, `skills-network-learner`, 1Gi

OpenShift prerequisites: a project with OpenShift Pipelines installed, storage class `skills-network-learner`, and cluster resolver tasks `buildah` and `openshift-client` available in `openshift-pipelines`. The pipeline's service account must have permissions for image builds and deployments. Some older course clusters use ClusterTasks instead of the cluster resolver; adjust the two external task references to that platform if necessary.

```bash
oc apply -f .tekton/pvc.yml
oc apply -f .tekton/tasks.yml
oc apply -f .tekton/pipeline.yml

NAMESPACE="$(oc project -q)"
tkn pipeline start cicd-pipeline \
  -p repo-url="https://github.com/siddismyusername/ci-cd-final-project.git" \
  -p revision="main" \
  -p build-image="image-registry.openshift-image-registry.svc:5000/$NAMESPACE/cicd-app:latest" \
  -w name=source,claimName=oc-lab-pvc \
  --showlog
```

After the pipeline succeeds, verify the deployment and obtain real evidence:

```bash
oc get pvc oc-lab-pvc
oc get deployment cicd-app
oc rollout status deployment/cicd-app
oc logs deployment/cicd-app | tee oc-pipeline-application-logs
```

The `oc-pipeline-application-logs` file should contain the literal `SERVICERUNNING` message when the application starts.

## License and Attribution

Apache 2.0; based on the educational counter-service design and workflow exercises from [IBM Skills Network's CI/CD final project template](https://github.com/ibm-developer-skills-network/vselh-ci-cd-final-project-template). See [LICENSE](LICENSE).
