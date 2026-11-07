# Lab 6: REST vs gRPC

Times are in milliseconds per operation (average over many calls). Servers and clients
ran on e2-standard-2 VMs using internal IPs. Same-zone: both in us-west1-a. Different
region: client in us-west1-a, server in europe-west3-a (Frankfurt). Repetitions: 1000 for
add and dotproduct and 100 for the image calls (locally and same-zone), and 100 for
every call cross-region.

| Method | Local | Same-Zone | Different Region |
|--- |--- |--- |--- |
| REST add | 2.56 | 3.25 | 309.75 |
| gRPC add | 0.80 | 1.25 | 161.71 |
| REST rawimg | 6.50 | 8.47 | 1589.21 |
| gRPC rawimg | 12.31 | 14.49 | 193.23 |
| REST dotproduct | 3.06 | 3.89 | 309.13 |
| gRPC dotproduct | 0.85 | 1.31 | 150.20 |
| REST jsonimg | 41.68 | 39.98 | 1480.92 |
| gRPC jsonimg | 32.92 | 34.57 | 217.94 |
| PING | 0.049 | 0.341 | 151.25 |

## Observations

**Network latency.** The ping row is the floor: about 0.05 ms locally, 0.34 ms in the
same zone, and 151 ms to Frankfurt. REST makes a new TCP connection for every query, so
each call pays about two round trips (handshake plus request/response). That matches REST
add and dotproduct at about 310 ms, roughly 2 x 151 ms. gRPC reuses one connection, so
each call pays about one round trip: gRPC add and dotproduct took about 150 to 160 ms.
Across regions, latency dominates everything else.

**Small messages.** For add and dotproduct, gRPC was about 3x faster than REST locally
and in the same zone, where the per-request overhead (new connection, text/JSON handling)
is a large share of the total.

**Large images.** The results depended on distance. Locally and in the same zone, gRPC was
slower than REST for rawimg (12.31 vs 6.50 ms), which I did not expect. A possible reason
is that gRPC in Python is not designed for very large messages and splits the 1.6 MB
payload into many pieces. Across regions, gRPC was far faster (193 vs 1589 ms), probably
because its single long-lived connection avoids repeated connection setup and reaches full
transfer speed. jsonimg was slower than rawimg because base64 makes the payload about a
third bigger and adds encode and decode work. These are single runs, so small differences
may be noise.
