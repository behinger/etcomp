/*
 * This file is part of cosy-zeromq-matlab.
 *
 * Copyright (C) 2016 - Université Catholique de Louvain
 *
 * cosy-zeromq-matlab is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or (at your
 * option) any later version.
 *
 * cosy-zeromq-matlab is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
 * for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with cosy-zeromq-matlab.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Author: Sébastien Wilmet
 */

/* ZeroMQ subscriber wrapper for Matlab */

#include <string.h>
#include <assert.h>
#include <mex.h>
#include <zmq.h>

#include "utils.h"
#include "multi_connector.h"

/* Support multiple initializations, because if the Matlab script crashes, the
 * the mex isn't unloaded.
 */
static MultiConnector *connector = NULL;

static void
close_zmq (void)
{
	if (connector != NULL)
	{
		multi_connector_free (connector);
		connector = NULL;
	}
}

static void
print_error (const char *msg)
{
	/* Clean-up before exit, so hopefully the Matlab script can be run again
	 * without restarting Matlab.
	 */
	close_zmq ();

	mexErrMsgTxt (msg);
}

static void
init_zmq (void)
{
	close_zmq ();

	assert (connector == NULL);
	connector = multi_connector_new ();
}

static int
add_subscriber (const char *end_point)
{
	return multi_connector_add_socket (connector, ZMQ_SUB, end_point);
}

static void
add_filter (int subscriber_id,
	    const char *filter)
{
	void *subscriber;
	int ok;

	if (!multi_connector_valid_socket_id (connector, subscriber_id))
	{
		mexPrintf ("Invalid subscriber ID.\n");
		return;
	}

	subscriber = multi_connector_get_socket (connector, subscriber_id);
	assert (subscriber != NULL);

	ok = zmq_setsockopt (subscriber, ZMQ_SUBSCRIBE, filter, strlen (filter));
	if (ok != 0)
	{
		print_error ("zmq_subscriber error: impossible to set filter.");
	}
}

void
mexFunction (int n_return_values,
	     mxArray *return_values[],
	     int n_args,
	     const mxArray *args[])
{
	char *command;
	int i;

	if (n_args < 1)
	{
		print_error ("zmq_subscriber error: you must provide the command name and the arguments.");
	}

	command = mxArrayToString (args[0]);

	for (i = 0; command[i] != '\0'; i++)
	{
		command[i] = tolower (command[i]);
	}

	if (strcmp (command, "init") == 0)
	{
		if (n_return_values > 0)
		{
			print_error ("zmq_subscriber error: init command: "
				     "you cannot assign a result with this call.");
		}

		if (n_args > 1)
		{
			print_error ("zmq_subscriber error: init command: too many arguments.");
		}

		init_zmq ();
	}
	else if (strcmp (command, "add_subscriber") == 0)
	{
		char *end_point;
		int subscriber_id;
		int *ret_data;

		if (n_return_values > 1)
		{
			print_error ("zmq_subscriber error: add_subscriber command: "
				     "you cannot assign the result to more than one return variable.");
		}

		if (n_args > 2)
		{
			print_error ("zmq_subscriber error: add_subscriber command: too many arguments.");
		}

		end_point = mxArrayToString (args[1]);

		subscriber_id = add_subscriber (end_point);

		return_values[0] = mxCreateNumericMatrix (1, 1, mxINT32_CLASS, mxREAL);
		ret_data = (int *) mxGetData (return_values[0]);
		*ret_data = subscriber_id;

		mxFree (end_point);
	}
	else if (strcmp (command, "add_filter") == 0)
	{
		int subscriber_id;
		char *filter;

		if (n_return_values > 0)
		{
			print_error ("zmq_subscriber error: add_filter command: "
				     "you cannot assign a result with this call.");
		}

		if (n_args > 3)
		{
			print_error ("zmq_subscriber error: add_filter command: too many arguments.");
		}

		subscriber_id = utils_get_socket_id (args[1]);

		if (mxGetClassID (args[2]) != mxCHAR_CLASS)
		{
			print_error ("zmq_subscriber error: add_filter command: "
				     "the filter argument has an invalid type, it should be a string.");
		}

		filter = mxArrayToString (args[2]);

		add_filter (subscriber_id, filter);

		mxFree (filter);
	}
	else if (strcmp (command, "receive_next_message") == 0)
	{
		double *arg_data;
		int subscriber_id;
		double timeout;
		char *msg;

		if (n_return_values > 1)
		{
			print_error ("zmq_subscriber error: receive_next_message command: "
				     "you cannot assign the result to more than one return variable.");
		}

		if (n_args > 3)
		{
			print_error ("zmq_subscriber error: receive_next_message command: "
				     "too many arguments.");
		}

		subscriber_id = utils_get_socket_id (args[1]);

		/* It seems that numeric types from Matlab are encoded as
		 * doubles, even if there is no decimal separator (e.g. 3000).
		 */
		if (mxGetClassID (args[2]) != mxDOUBLE_CLASS)
		{
			print_error ("zmq_subscriber error: receive_next_message command: "
				     "the timeout has an invalid type, it should be a double.");
		}

		arg_data = (double *) mxGetData (args[2]);
		timeout = *arg_data;

		msg = multi_connector_receive_next_message (connector, subscriber_id, timeout);

		if (msg != NULL)
		{
			return_values[0] = mxCreateString (msg);
		}
		else
		{
			return_values[0] = mxCreateDoubleScalar (mxGetNaN ());
		}

		free (msg);
	}
	else if (strcmp (command, "close") == 0)
	{
		if (n_return_values > 0)
		{
			print_error ("zmq_subscriber error: close command: "
				     "you cannot assign a result with this call.");
		}

		if (n_args > 1)
		{
			print_error ("zmq_subscriber error: close command: too many arguments.");
		}

		close_zmq ();
	}
	else
	{
		print_error ("zmq_subscriber error: unknown command.");
	}

	mxFree (command);
}
