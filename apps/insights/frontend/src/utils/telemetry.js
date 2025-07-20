import { useStorage } from '@/vueuse/core'
import { call } from 'frappe-ui'
import '../../../frappe/public/js/lib/posthog.js'

const APP = 'insights'
const SITENAME = window.location.hostname

const telemetry = useStorage('insights:telemetry', {
	enabled: false,
	project_id: undefined,
	telemetry_host: undefined,
})

async function initialize() {
	await set_enabled()
	if (!telemetry.enabled) return
	try {
		await set_credentials()
		posthog.init(telemetry.project_id, {
			api_host: telemetry.telemetry_host,
			autocapture: false,
			capture_pageview: false,
			capture_pageleave: false,
			advanced_disable_decide: true,
		})
		posthog.identify(SITENAME)
	} catch (e) {
		console.trace('Failed to initialize telemetry', e)
		telemetry.enabled = false
	}
}
async function set_enabled() {
	if (telemetry.enabled) return
	return await call('insights.api.telemetry.is_enabled').then((res) => {
		telemetry.enabled = res
	})
}
async function set_credentials() {
	if (!telemetry.enabled) return
	if (telemetry.project_id && telemetry.telemetry_host) return
	return await call('insights.api.telemetry.get_credentials').then((res) => {
		telemetry.project_id = res.project_id
		telemetry.telemetry_host = res.telemetry_host
	})
}
function capture(event) {
	if (!telemetry.enabled) return
	posthog.capture(`${APP}_${event}`)
}
function disable() {
	telemetry.enabled = false
	posthog.opt_out_capturing()
}

export default {
	initialize,
	capture,
	disable,
}
