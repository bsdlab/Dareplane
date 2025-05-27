README := main.qmd 
CSV_FILE := modules.csv
MODULES_DIR := modules
DOCS_GALLERY := modules/gallery.yml
DEFAULT_THUMBNAIL := assets/single_dareplane_logo.svg

.PHONY: all quartodoc build publish clean dp-docs main

# -----------------------------------------------------------------------------
# main.qmd from the central README.md
# -----------------------------------------------------------------------------

main:
	@echo "Copying over ../README.md to main.qmd and replacing the logo image section..."
	@awk -v header="::: {.light-content}\n{{< brand logo large light>}}\n:::\n::: {.dark-content}\n{{< brand logo large dark>}}\n:::\n" ' \
  BEGIN { print header } \
  /<\/picture>/ { found=1; next } \
  found { print } ' ../README.md > main.qmd
	

# -----------------------------------------------------------------------------
# Single modules parsing
# -----------------------------------------------------------------------------

# Extract first markdown table and convert to CSV
$(CSV_FILE): $(README)
	@echo 'Extracting table from $(README)..'
	@awk '/^\|/,/^\s*$$/ {if ($$0 ~ /^\|/) print $$0}' $(README) \
	| sed 's/^|//; s/|$$//; s/|/,/g; s/^ *//; s/ *$$//' \
	| grep -v '^,\+,$$' > $@


# -----------------------------------------------------------------------------
# Downloading and quartodoc generation
# -----------------------------------------------------------------------------
#
# Extract markdown links from first CSV column
REPOS := $(shell awk -F ',' 'NR > 2 { \
	if ($$1 ~ /\[.*\]\(.*\)/) {  \
		split($$1, parts, /\]/); \
    print parts[2]; \
       } \
   }' modules.csv 2>/dev/null | tr -d '()')   # supress error when run before the CSV_FILE is built
REPO_NAMES := $(foreach repo,$(REPOS),$(notdir $(repo:.git=)))
REPO_DIRS := $(addprefix $(MODULES_DIR)/,$(REPO_NAMES))


dp-docs: $(REPO_DIRS) $(REPOS_CSV)

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

# -----------------------------------------------------------------------------
# Populating the gallery for docs
# -----------------------------------------------------------------------------
docs-gallery: $(DOCS_GALLERY) $(REPO_DIRS)

$(DOCS_GALLERY): $(REPO_DIRS)
	@echo "Generating documentation gallery..."
	@echo "- category: Utility librarires" >> $@
	@echo "  description: Collection of libraries providing functionality to Dareplane" >> $@
	@echo "  tiles:" >> $@
	@echo "    - title: dareplane-utils" >> $@
	@echo "      description: Python module with various utility functions for Dareplane modules" >> $@
	@echo "      href: ../libraries/dareplane_utils/index.qmd" >> $@
	@echo "      thumbnail: ../$(DEFAULT_THUMBNAIL)" >> $@
	@echo "- category: Single module documentation" >> $@
	@echo "  description: \"Dareplane is structured in individual module, each providing its own documentation\"" >> $@
	@echo "  tiles:" >> $@
	@for repo in $(REPO_DIRS); do \
		REPO_NAME=$$(basename $$repo); \
		THUMBNAIL=$$(if [ -f "$$repo/assets/thumbnail.png" ]; then echo "$$REPO_NAME/assets/thumbnail.png"; else echo "../$(DEFAULT_THUMBNAIL)"; fi); \
		echo "    - title: $$REPO_NAME" >> $@; \
		echo "      href: $$REPO_NAME/reference/index.qmd" >> $@; \
		echo "      thumbnail: $$THUMBNAIL" >> $@; \
	done

	@echo "Gallery YAML generated at $@"

# # -- No need for the copy step as quarto can deal with recursive wild-card for adding content to the main page
# 	# @if [ -d "$(MODULES_DIR)/$*/reference" ]; then \
# 	# 	echo "Syncing documentation..."; \
# 	# 	mkdir -p "modules_docs/$*"; \
# 	# 	rsync -av --delete "$(MODULES_DIR)/$*/reference/" "modules_docs/$*"; \
# 	# else \
# 	# 	echo "Error: Reference directory missing after build"; \
# 	# 	exit 1; \
# 	# fi
# 	#

# ----------------------------------------------------------------------------
# General utility
# -----------------------------------------------------------------------------

clean:
	rm -f $(CSV_FILE)
	rm -rf _site reference
	rm -rf modules/dp-*
	rm -rf modules/gallery.yml
	rm -f main.qmd

quartodoc:
	quartodoc

build:
	quartodoc build
	quarto preview

publish:
	quarto publish gh-pages
