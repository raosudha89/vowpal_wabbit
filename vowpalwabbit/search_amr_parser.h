#pragma once
#include "search.h"

namespace AMRParserTask
{
void initialize(Search::search&, size_t&, po::variables_map&);
void finish(Search::search&);
void run(Search::search&, vector<example*>&);
void setup(Search::search&, vector<example*>&);
extern Search::search_task task;
}
