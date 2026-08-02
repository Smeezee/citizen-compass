# UPDATE — Part A behaviour probe

Test file dropped to determine which watcher is live. If only
logs/inbox_watcher.log gains a line and pipeline_log.txt does not, the Go
watcher is the sole writer and the stray Python watcher is gone.
