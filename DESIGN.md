## Q1. If the number of jobs reaches 1 million per day:

### How would the current system be affected?

At this scale, several bottlenecks may appear:

- A single scheduler instance would become a throughput bottleneck because it is responsible for claiming pending jobs from the database.
- Four worker threads would no longer be sufficient to process all incoming jobs in a timely manner.
- The `jobs` table would continuously grow, increasing storage requirements and making database maintenance (vacuuming, indexing, backups, etc.) more expensive.
- A single machine would eventually become insufficient in terms of CPU, memory, and storage resources.

### What changes would you make?

#### 1. Horizontally shard the system

I would shard jobs across multiple machines using the `job_id` (UUID) as the sharding key. This approach allows jobs to be distributed evenly across nodes while making routing deterministic. Since the client already owns the job ID, the API can efficiently route `GET /jobs/{job_id}` requests to the machine responsible for that shard.

#### 2. Scale the schedulers and workers horizontally

The current implementation contains a single scheduler that polls pending jobs every second. I would deploy multiple scheduler instances across different machines. Since jobs are claimed using `FOR UPDATE SKIP LOCKED`, schedulers do not block each other or process the same job twice, allowing them to safely work in parallel.

Each scheduler owns a bounded worker pool. Depending on the available hardware resources, the number of worker threads can be increased, and each scheduler can claim larger batches of jobs in every polling cycle to improve throughput.

#### 3. Introduce a dedicated message broker

If the workload continues to increase beyond what a database-backed queue can efficiently handle, I would replace the PostgreSQL queue with a dedicated message broker such as Kafka.

In this architecture, schedulers would publish newly claimed jobs to Kafka partitions. Since job ordering is not important for this use case, no custom partitioning key is required, allowing Kafka to distribute messages evenly across partitions. Multiple consumer groups (running on several machines, each with multiple worker instances) would process jobs concurrently, providing significantly higher throughput, better horizontal scalability, and improved fault tolerance.


## Q2. If processing each job takes 30 seconds:

### What architectural changes would you make?

The current architecture is already asynchronous, so increasing the execution time of a job does not affect the response time of the API. Clients still receive the job identifier immediately while processing continues in the background. In other words, the asynchronous architecture already isolates request latency from job execution time.

However, increasing the execution time to 30 seconds significantly reduces the system's throughput. For example, with a worker pool of four workers, the maximum theoretical throughput is approximately **4 / 30 ≈ 0.13 jobs per second**. Therefore, the primary challenge becomes **throughput**. The API latency remains unchanged, while the job completion latency increases because jobs spend more time waiting in the queue before being processed.

To address this, I would first scale the existing architecture horizontally by increasing the size of the worker pool (for example, from 4 to 8, 16, or 32 workers, depending on the available hardware resources) or by deploying additional scheduler/worker instances on multiple machines. Since jobs are claimed atomically using `FOR UPDATE SKIP LOCKED`, multiple scheduler instances can safely operate in parallel without processing the same job twice.

If the workload continues to grow beyond what a database-backed queue can efficiently support, I would evolve the architecture by replacing the PostgreSQL queue with a dedicated message broker such as Kafka or RabbitMQ. This allows producers and consumers to scale independently while providing higher throughput and improved fault tolerance.

## Q3. If multiple instances of the service are running:

### How would you manage the state of jobs?

The application instances themselves remain stateless. The state of every job (`pending`, `processing`, `completed`, or `failed`) is stored in PostgreSQL, making the database the single source of truth. This allows any service instance to serve client requests without relying on in-memory state.

When a scheduler instance looks for new jobs, it atomically claims them using `FOR UPDATE SKIP LOCKED` and immediately changes their status from `pending` to `processing` within the same transaction. This guarantees that a job can only be claimed by one scheduler instance, preventing duplicate processing and race conditions.

After processing is complete, the worker updates the job status to either `completed` or `failed`. Since all state transitions are persisted in the database, any application instance can respond to `GET /jobs/{job_id}` requests by reading the current job status from PostgreSQL.

This architecture allows multiple application instances to scale horizontally while maintaining a consistent view of job state without requiring distributed locks or shared in-memory storage.