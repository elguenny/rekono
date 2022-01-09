import RekonoApi from './api'

class Process extends RekonoApi {
  getAllProcesses (filter = null) {
    return super.getAllPages('/api/processes/?o=-likes_count,name', filter)
  }

  getPaginatedProcesses (page = null, limit = null, filter = null) {
    return super.get('/api/processes/?o=-likes_count,name', page, limit, filter)
      .then(response => {
        return response.data
      })
  }

  createProcess (name, description, tags = []) {
    const data = {
      name: name,
      description: description,
      tags: tags
    }
    return super.post('/api/processes/', data)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  updateProcess (processId, name, description, tags = []) {
    const data = {
      name: name,
      description: description,
      tags: tags
    }
    return super.put(`/api/processes/${processId}/`, data)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  deleteProcess (processId) {
    return super.delete(`/api/processes/${processId}/`)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }
}

class Step extends RekonoApi {
  createStep (processId, toolId, configurationId, priority) {
    const data = {
      process: processId,
      tool_id: toolId,
      configuration_id: configurationId,
      priority: priority
    }
    return super.post('/api/steps/', data)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  updateStep (stepId, priority) {
    const data = {
      priority: priority
    }
    return super.put(`/api/steps/${stepId}/`, data)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }

  deleteStep (stepId) {
    return super.delete(`/api/steps/${stepId}/`)
      .then(response => {
        return Promise.resolve(response.data)
      })
  }
}

export default {
  ProcessApi: new Process(),
  StepApi: new Step()
}