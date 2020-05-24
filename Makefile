#!/bin/sh

MOD_NAME=asynchronous_application_python3

MOD_VERSION=1.0.2

PACKAGE_NAME=$(MOD_NAME)-$(MOD_VERSION)

PLATFORM_VERSION := $(shell uname -r| awk -F 'el' '{printf("%d", substr($$2,1,1))}')

PROMETHEUS_DIR := $(CURDIR)/.prometheus_multiproc_dir
export prometheus_multiproc_dir=$(PROMETHEUS_DIR)
#Set port; please change this value as you want.
PORT := 8080

.PHONY: package clean

req:
	if [ ! -d "$(PROMETHEUS_DIR)" ]; then \
        mkdir -p  $(PROMETHEUS_DIR) ;\
    else \
        rm -f $(PROMETHEUS_DIR)/* ; \
    fi


start: req
	nohup python3 main.py --port=$(PORT) >> ./log/server.log 2>&1 &

stop:
	ps aux | grep 'main' | grep -v grep | grep 'port' | awk '{print $$2}' | xargs kill -9

help:
	echo "usage: ./main.py --port={port} &"

clean:
	rm -rf log/*
	rm -rf packages

#install with python>=3.0
install:
	pip install -r ./conf/requirements.txt

package: clean
	@if test ! -d packages/$(PACKAGE_NAME); then \
		mkdir -p packages/$(PACKAGE_NAME); \
	else \
	    rm -rf packages/$(PACKAGE_NAME); \
	    mkdir -p packages/$(PACKAGE_NAME); \
	fi
	mkdir -p packages/$(PACKAGE_NAME)/common
	mkdir -p packages/$(PACKAGE_NAME)/conf
	mkdir -p packages/$(PACKAGE_NAME)/demo
	mkdir -p packages/$(PACKAGE_NAME)/log
	mkdir -p packages/$(PACKAGE_NAME)/tools
	cp -fr ./*.py packages/$(PACKAGE_NAME)
	cp -r ./common/* packages/$(PACKAGE_NAME)/common
	cp -r ./conf/* packages/$(PACKAGE_NAME)/conf
	cp -r ./demo/* packages/$(PACKAGE_NAME)/demo
	cp -r ./tools/* packages/$(PACKAGE_NAME)/tools
	cp -r Makefile packages/$(PACKAGE_NAME)
	cp -r README.md packages/$(PACKAGE_NAME)
	tar zcf packages/$(MOD_NAME)-$(PLATFORM_VERSION)-$(MOD_VERSION).tgz -C packages $(PACKAGE_NAME)

	

