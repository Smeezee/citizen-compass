module citizencompass/watcher

go 1.26.5

require (
	citizencompass/pkg/apikeyguard v0.0.0
	citizencompass/pkg/pipelinelog v0.0.0
	github.com/fsnotify/fsnotify v1.10.1 // indirect
	golang.org/x/image v0.44.0 // indirect
	golang.org/x/sys v0.13.0 // indirect
)

replace citizencompass/pkg/apikeyguard => ../pkg/apikeyguard

replace citizencompass/pkg/pipelinelog => ../pkg/pipelinelog
