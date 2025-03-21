/*-
 *   BSD LICENSE
 *
 *   Copyright (c) Intel Corporation. All rights reserved.
 *   Copyright (c) 2019 Mellanox Technologies LTD. All rights reserved.
 *
 *   Redistribution and use in source and binary forms, with or without
 *   modification, are permitted provided that the following conditions
 *   are met:
 *
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in
 *       the documentation and/or other materials provided with the
 *       distribution.
 *     * Neither the name of Intel Corporation nor the names of its
 *       contributors may be used to endorse or promote products derived
 *       from this software without specific prior written permission.
 *
 *   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 *   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 *   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 *   A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 *   OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 *   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 *   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 *   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 *   THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 *   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 *   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include "spdk/stdinc.h"

#include "spdk/event.h"
#include "spdk/rpc.h"
#include "spdk/string.h"
#include "spdk/util.h"
#include "spdk/env.h"
#include "spdk/thread.h"

#include "spdk_internal/log.h"

struct rpc_kill_instance {
	char *sig_name;
};

static void
free_rpc_kill_instance(struct rpc_kill_instance *req)
{
	free(req->sig_name);
}

static const struct spdk_json_object_decoder rpc_kill_instance_decoders[] = {
	{"sig_name", offsetof(struct rpc_kill_instance, sig_name), spdk_json_decode_string},
};

static void
spdk_rpc_kill_instance(struct spdk_jsonrpc_request *request,
		       const struct spdk_json_val *params)
{
	static const struct {
		const char	*signal_string;
		int32_t		signal;
	} signals[] = {
		{"SIGINT",	SIGINT},
		{"SIGTERM",	SIGTERM},
		{"SIGQUIT",	SIGQUIT},
		{"SIGHUP",	SIGHUP},
		{"SIGKILL",	SIGKILL},
	};
	size_t i, sig_count;
	int signal;
	struct rpc_kill_instance req = {};
	struct spdk_json_write_ctx *w;

	if (spdk_json_decode_object(params, rpc_kill_instance_decoders,
				    SPDK_COUNTOF(rpc_kill_instance_decoders),
				    &req)) {
		SPDK_DEBUGLOG(SPDK_LOG_REACTOR, "spdk_json_decode_object failed\n");
		goto invalid;
	}

	sig_count = SPDK_COUNTOF(signals);
	signal = spdk_strtol(req.sig_name, 10);
	for (i = 0 ; i < sig_count; i++) {
		if (strcmp(req.sig_name, signals[i].signal_string) == 0 ||
		    signal == signals[i].signal) {
			break;
		}
	}

	if (i == sig_count) {
		goto invalid;
	}

	SPDK_DEBUGLOG(SPDK_LOG_REACTOR, "sending signal %d\n", signals[i].signal);
	free_rpc_kill_instance(&req);
	kill(getpid(), signals[i].signal);

	w = spdk_jsonrpc_begin_result(request);
	if (w == NULL) {
		return;
	}
	spdk_json_write_bool(w, true);
	spdk_jsonrpc_end_result(request, w);
	return;

invalid:
	spdk_jsonrpc_send_error_response(request, SPDK_JSONRPC_ERROR_INVALID_PARAMS, "Invalid parameters");
	free_rpc_kill_instance(&req);
}
SPDK_RPC_REGISTER("kill_instance", spdk_rpc_kill_instance, SPDK_RPC_RUNTIME)


struct rpc_context_switch_monitor {
	bool enabled;
};

static const struct spdk_json_object_decoder rpc_context_switch_monitor_decoders[] = {
	{"enabled", offsetof(struct rpc_context_switch_monitor, enabled), spdk_json_decode_bool},
};

static void
spdk_rpc_context_switch_monitor(struct spdk_jsonrpc_request *request,
				const struct spdk_json_val *params)
{
	struct rpc_context_switch_monitor req = {};
	struct spdk_json_write_ctx *w;

	if (params != NULL) {
		if (spdk_json_decode_object(params, rpc_context_switch_monitor_decoders,
					    SPDK_COUNTOF(rpc_context_switch_monitor_decoders),
					    &req)) {
			SPDK_DEBUGLOG(SPDK_LOG_REACTOR, "spdk_json_decode_object failed\n");
			spdk_jsonrpc_send_error_response(request, SPDK_JSONRPC_ERROR_INVALID_PARAMS, "Invalid parameters");
			return;
		}

		spdk_reactor_enable_context_switch_monitor(req.enabled);
	}

	w = spdk_jsonrpc_begin_result(request);
	if (w == NULL) {
		return;
	}

	spdk_json_write_object_begin(w);

	spdk_json_write_named_bool(w, "enabled", spdk_reactor_context_switch_monitor_enabled());

	spdk_json_write_object_end(w);
	spdk_jsonrpc_end_result(request, w);
}

SPDK_RPC_REGISTER("context_switch_monitor", spdk_rpc_context_switch_monitor, SPDK_RPC_RUNTIME)

struct rpc_thread_get_stats_ctx {
	struct spdk_jsonrpc_request *request;
	struct spdk_json_write_ctx *w;
};

static void
rpc_thread_get_stats_done(void *arg)
{
	struct rpc_thread_get_stats_ctx *ctx = arg;

	spdk_json_write_array_end(ctx->w);
	spdk_json_write_object_end(ctx->w);
	spdk_jsonrpc_end_result(ctx->request, ctx->w);

	free(ctx);
}

static void
rpc_thread_get_stats(void *arg)
{
	struct rpc_thread_get_stats_ctx *ctx = arg;
	struct spdk_thread_stats stats;

	if (0 == spdk_thread_get_stats(&stats)) {
		spdk_json_write_object_begin(ctx->w);
		spdk_json_write_named_string(ctx->w, "name", spdk_thread_get_name(spdk_get_thread()));
		spdk_json_write_named_uint64(ctx->w, "busy", stats.busy_tsc);
		spdk_json_write_named_uint64(ctx->w, "idle", stats.idle_tsc);
		spdk_json_write_object_end(ctx->w);
	}
}

static void
spdk_rpc_thread_get_stats(struct spdk_jsonrpc_request *request,
			  const struct spdk_json_val *params)
{
	struct rpc_thread_get_stats_ctx *ctx;

	if (params) {
		spdk_jsonrpc_send_error_response(request, SPDK_JSONRPC_ERROR_INVALID_PARAMS,
						 "'thread_get_stats' requires no arguments");
		return;
	}

	ctx = calloc(1, sizeof(*ctx));
	if (!ctx) {
		spdk_jsonrpc_send_error_response(request, SPDK_JSONRPC_ERROR_INTERNAL_ERROR,
						 "Memory allocation error");
		return;
	}
	ctx->request = request;

	ctx->w = spdk_jsonrpc_begin_result(ctx->request);
	if (NULL == ctx->w) {
		free(ctx);
		return;
	}
	spdk_json_write_object_begin(ctx->w);
	spdk_json_write_named_uint64(ctx->w, "tick_rate", spdk_get_ticks_hz());
	spdk_json_write_named_array_begin(ctx->w, "threads");

	spdk_for_each_thread(rpc_thread_get_stats, ctx, rpc_thread_get_stats_done);
}

SPDK_RPC_REGISTER("thread_get_stats", spdk_rpc_thread_get_stats, SPDK_RPC_RUNTIME)
