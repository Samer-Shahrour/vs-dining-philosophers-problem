# Distributed Dining Philosophers (Docker + Custom RPC)

## Overview
This repository contains a group project for a Distributed Systems course.  
We implemented a distributed solution to the classic Dining Philosophers problem using Docker containers and a custom RPC Solution.  

The system ensures deadlock-free execution by assigning philosophers different "handedness":  
- Some philosophers pick up their left fork first.  
- Others pick up their right fork first.  

This breaks circular waiting and guarantees that all philosophers eventually get to eat.

---

## Features
- Distributed execution with **Docker containers**.  
- **Custom RPC** implementation for communication.  
- **Deadlock avoidance** using handedness strategy.  
- Collaborative design and implementation as a **group project**.  
- Modular setup for experimenting with distributed coordination.
