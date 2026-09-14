module citizencompass/rsiwatcher

go 1.26.5

require (
	citizencompass/pkg/apikeyguard v0.0.0
	citizencompass/pkg/pipelinelog v0.0.0
)

require golang.org/x/sys v0.48.0 // indirect

replace citizencompass/pkg/apikeyguard => ../pkg/apikeyguard

replace citizencompass/pkg/pipelinelog => ../pkg/pipelinelog
