# CoCo Serverless

The goal of this project is to deploy Knative on CoCo and run some baseline benchmarks.

All instructions in this repository assume that you have checked-out the source code, and have activated the python virtual environment:

```bash
source ./bin/workon.sh

# List available tasks
inv -l
```

## Pre-Requisites

You will need CoCo's fork of containerd built and running. To this extent you
may run:

```bash
inv containerd.build
inv containerd.install
```

You also need all the kubernetes-related tooling: `kubectl`, `kubeadm`, and
`kubelet`:

```bash
inv k8s.install [--clean]
```

## Quick Start

Deploy a (single-node) kubernetes cluster using `kubeadm`:

```bash
inv kubeadm.create
```

Second, install both the operator and the CC runtime from the upstream tag.
We currently pin to version `v0.7.0` (see the [`COCO_RELEASE_VERSION` variable](https://github.com/csegarragonz/coco-serverless/tree/main/tasks/util/env.py)).

```bash
inv operator.install
inv operator.install-cc-runtime
```

Then, you are ready to run one of the supported apps:
* [Hello World! (Py)](./docs/helloworld_py.md) - simple HTTP server running in Python to test CoCo and Kata.
* [Hello World! (Knative)](./docs/helloworld_knative.md) - same app as before, but invoked over Knatvie.

If your app uses Knative, you will have to install it first:

```bash
inv knative.install
```

## Uninstall

In order to uninstall components for debugging purposes, you may un-install the CoCo runtime, and then the operator as follows:

```bash
inv operator.uninstall-cc-runtime
inv operator.uninstall
```

Lastly, you can completely remove the `k8s` cluster by running:

```bash
inv kubeadm.destroy
```

## Further Reading

For further documentation, you may want to check these other documents:
* [Knative](./docs/knative.md) - documentation about Knative, our serverless runtime of choice.
* [SEV](./docs/sev.md) - speicifc documentation to get the project working with AMD SEV machines.
