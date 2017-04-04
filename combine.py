import glob

def combine_edit_logs():
	path = "~/WikiAnalysis/Wikidumps/Output_Logs/"
	files_to_combine = glob.glob("edits_*")
	print(files_to_combine)
	with open("edits_.log","wb") as file_to_write:
		for file in files_to_combine:
			with open(file, "rb") as file_to_read:
				file_to_write.write(file_to_read.read())


def combine_revert_logs():
	path = "~/WikiAnalysis/Wikidumps/Output_Logs/"
	files_to_combine = glob.glob("reverts_*")
	print(files_to_combine)
	with open("reverts_.log","wb") as file_to_write:
		for file in files_to_combine:
			with open(file, "rb") as file_to_read:
				file_to_write.write(file_to_read.read())

def remove_pages_without_revision_ids():
	path = "~/WikiAnalysis/Wikidumps/Output_Logs/"
	file_to_read = open("reverts_.log", "rb")
	file_to_write = open("mod_reverts_.log", "wb")

	total_page_ids = 0
	for line in file_to_read:
		if line[0] == "#":
			total_page_ids += 1
			str = line
			
		

	file_to_read.close()
	file_to_write.close()



def main():
	combine_edit_logs()
	combine_revert_logs()

main()
