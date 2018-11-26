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

#ifndef COSY_ZMQ_MULTI_CONNECTOR_H
#define COSY_ZMQ_MULTI_CONNECTOR_H

typedef struct _MultiConnector MultiConnector;

MultiConnector *	multi_connector_new			(void);

void			multi_connector_free			(MultiConnector *connector);

int			multi_connector_add_socket		(MultiConnector *connector,
								 int socket_type,
								 const char *end_point);

int			multi_connector_valid_socket_id		(MultiConnector *connector,
								 int socket_id);

void *			multi_connector_get_socket		(MultiConnector *connector,
								 int socket_id);

char *			multi_connector_receive_next_message	(MultiConnector *connector,
								 int socket_id,
								 double timeout);

#endif /* COSY_ZMQ_MULTI_CONNECTOR_H */
