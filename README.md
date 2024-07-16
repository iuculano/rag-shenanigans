# RAG shenanigans

Misadventures in trying to minimize "garbage in" to the model and experiments in trying to chunk more in a more intelligent way. Essentially, the goal is to minimize, as much as possible, sending any and all irrelevant data.

* https://github.com/aws-samples/layout-aware-document-processing-and-retrieval-augmented-generation
* https://www.reddit.com/r/LangChain/comments/1dtr49t/agent_rag_parallel_quotes_how_we_built_rag_on/
* https://techcommunity.microsoft.com/t5/microsoft-developer-community/doing-rag-vector-search-is-not-enough/ba-p/4161073

## What works (in a hacked together in a weekend way)

Half the magic is in the splitter. It is intended to produce sentence sized vectors.

To accomplish this, it will:

1. First, split a document on “sections” and assign an ID to each.
2. Each section is split into sentences - these are our chunks/vectors.

	The following metadata is associated with each sentence/chunk.

	1. The document name
	2. The ID of the section it belongs to
	3. The position of this chunk in the document
	4. The ending position of the document

After retrieving a chunk, the document can be reconstructed from the starting
position of that chunk to the end of the section. This is done to try to avoid
pulling in any irrelevant data with more arbitrary chunking strategies. Data
within a section (hopefully) has a higher chance of being relevant than a chunk
that may have landed between two sections.

It's possible that retrieval may return multiple chunks within a section, so to
cope, I deduplicate by calculating the minimum position for all chunks within a
section. An ID is assigned to each section for handling deduplication.

This effectively produces one span per section, representing the substring that
is needed.

## Where we're going

To stay with the goal of minimizing irrelevant data being sent to the model, the
resultant spans will be passed to a model (GPT 3.5?) for it to pick out quotes
it believes are relevant to the question. This should happen in parallel for
numerous sections for performance sake.

The goal is to produce _only quotes that appear relevant_ and _no superfluous
data_. After all these requests return, we’ll join them to produce the list that
is handed off for the actual question answering.

From a backend perspective, I think requests to the model should:

1. Be resilient
2. Be scalable

A message queue architecture is appealing. We can scale "workers" by messages in
the queue, and (ideally) get nice, elastic scalability.

Any worker should be able to handle any request - we don't want to bind workers
to particular models or users. They should be stateless.

If we need to reconstruct the document, where does it come from?

1. Stream from object storage?
2. (Ab)use Postgres and directly query substrings?
3. Cache in Redis?
