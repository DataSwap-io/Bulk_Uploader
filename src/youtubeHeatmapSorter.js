function getTopReplayedParts(data, parts) {
  if (!data || !data.markers) {
    return []
  }

  const sortedMarkers = data.markers.sort(
    (a, b) => b.intensityScoreNormalized - a.intensityScoreNormalized,
  )

  const topMarkers = sortedMarkers.slice(0, parts)

  return topMarkers.map((marker, index) => ({
    position: index + 1,
    start: Math.round(Number(marker.startMillis) / 1000),
    end: Math.round(
      (Number(marker.startMillis) + Number(marker.durationMillis)) / 1000,
    ),
  }))
}

module.exports = {
  getTopReplayedParts,
}
