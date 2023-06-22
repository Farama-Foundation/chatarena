#!/bin/bash
# while there are files in the todo directory
while [ "$(ls -A env_logs/todo/)" ]; do
		# select one file from the todo directory
		# then move it to the done directory
		file_to_process=$(ls -1 env_logs/todo/ | head -n1)
		manim -qh conversation.py Conversation $(echo env_logs/todo/$file_to_process) && mv env_logs/todo/$file_to_process env_logs/done/$file_to_process
done
