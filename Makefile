# This file is only needed to build/publish a docker image for this project
# If you have python & pip installed, you can instead just run the code directly.

# To build the image into your local docker cache run `make latest`

REGISTRY=  exaspace
IMAGE    = rabbit-kafka-bridge
VERSION  = $(shell git describe || git rev-parse head)

DOCKER=$(shell docker info >/dev/null 2>&1 && echo "docker" || echo "sudo docker")

all: latest

build:
	$(DOCKER) build $(build_opts) -t $(REGISTRY)/$(IMAGE):$(VERSION) ./

latest: build
	$(DOCKER) tag $(REGISTRY)/$(IMAGE):$(VERSION) $(REGISTRY)/$(IMAGE):latest

push:
	$(DOCKER) push $(REGISTRY)/$(IMAGE):$(VERSION)
	$(DOCKER) push $(REGISTRY)/$(IMAGE):latest
