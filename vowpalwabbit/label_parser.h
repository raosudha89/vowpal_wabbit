#pragma once

#include "v_array.h"
#include "parse_primitives.h"
#include "io_buf.h"

struct parser;
struct shared_data;

struct label_parser
{ void (*default_label)(void*);
  void (*parse_label)(parser*, shared_data*, void*, v_array<substring>&);
  void (*cache_label)(void*, io_buf& cache);
  size_t (*read_cached_label)(shared_data*, void*, io_buf& cache);
  void (*delete_label)(void*);
  float (*get_weight)(void*);
  void (*copy_label)(void*,void*); // copy_label(dst,src) performs a DEEP copy of src into dst (dst is allocated correctly).  if this function is nullptr, then we assume that a memcpy of size label_size is sufficient, so you need only specify this function if your label constains, for instance, pointers (otherwise you'll get double-free errors)
  size_t label_size;
  bool operator==(const label_parser& other) const
  { return
        default_label == other.default_label &&
        parse_label == other.parse_label &&
        cache_label == other.cache_label &&
        read_cached_label == other.read_cached_label &&
        delete_label == other.delete_label &&
        get_weight == other.get_weight &&
        copy_label == other.copy_label &&
        label_size == other.label_size;
  }
};
