README := main.qmd 
CSV_FILE := modules.csv
MODULES_DIR := modules
MODULES_DOCS_DIR := modules_docs

# Extract first markdown table and convert to CSV
$(CSV_FILE): $(README)
	@echo 'Extracting table from $(README)..'
	@awk '/^\|/,/^\s*$$/ {if ($$0 ~ /^\|/) print $$0}' $(README) \
	| sed 's/^|//; s/|$$//; s/|/,/g; s/^ *//; s/ *$$//' \
	| grep -v '^,\+,$$' > $@

# Extract markdown links from first CSV column
REPOS := $(shell awk -F ',' 'NR > 2 { \
	if ($$1 ~ /\[.*\]\(.*\)/) {  \
		split($$1, parts, /\]/); \
    print parts[2]; \
       } \
   }' modules.csv | tr -d '()')
REPO_NAMES := $(foreach repo,$(REPOS),$(notdir $(repo:.git=)))
REPO_DIRS := $(addprefix $(MODULES_DIR)/,$(REPO_NAMES))

.PHONY: all quartodoc build publish clean print dp-docs

dp-docs: $(CSV_FILE) $(REPO_DIRS)

$(MODULES_DIR)/%:
	@echo "Cloning $*..."
	@mkdir -p $(MODULES_DIR)
	@cd $(MODULES_DIR) && git clone $(filter %$*,$(REPOS))
	@if [ -f $(MODULES_DIR)/$*/_quarto.yml ]; then \
		echo "Building documentation for $*..."; \
		cd $(MODULES_DIR)/$* && quartodoc build; \
	else \
		echo "No _quarto.yml found in $*, skipping documentation build"; \
	fi

# -- No need for the copy step as quarto can deal with recursive wild-card for adding content to the main page
	# @if [ -d "$(MODULES_DIR)/$*/reference" ]; then \
	# 	echo "Syncing documentation..."; \
	# 	mkdir -p "modules_docs/$*"; \
	# 	rsync -av --delete "$(MODULES_DIR)/$*/reference/" "modules_docs/$*"; \
	# else \
	# 	echo "Error: Reference directory missing after build"; \
	# 	exit 1; \
	# fi

clean:
	rm -rf $(MODULES_DIR)
	rm -f $(CSV_FILE)
	rm -rf _site reference
	rm -rf modules/*

quartodoc:
	quartodoc

build:
	quartodoc build
	quarto preview

publish:
	quarto publish gh-pages
