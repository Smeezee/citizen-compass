module citizencompass/roadmapwatcher

go 1.26.5

require (
	citizencompass/pkg/apikeyguard v0.0.0
	citizencompass/pkg/livever v0.0.0
	citizencompass/pkg/pipelinelog v0.0.0
)

replace citizencompass/pkg/apikeyguard => ../pkg/apikeyguard

replace citizencompass/pkg/livever => ../pkg/livever

replace citizencompass/pkg/pipelinelog => ../pkg/pipelinelog