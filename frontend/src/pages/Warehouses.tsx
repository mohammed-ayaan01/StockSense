import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { warehousesApi } from '../api'
import { LoadingSpinner, EmptyState } from '../components/States'
import { Plus, X } from 'lucide-react'

export default function Warehouses() {
  const qc = useQueryClient()
  const [selectedWH, setSelectedWH] = useState<number | null>(null)
  const [showWHForm, setShowWHForm] = useState(false)
  const [showLocForm, setShowLocForm] = useState(false)
  const [whForm, setWhForm] = useState({ name: '', code: '', address: '' })
  const [locForm, setLocForm] = useState({ warehouse_id: '', name: '', code: '', description: '' })

  const { data: warehouses = [], isLoading } = useQuery({ queryKey: ['warehouses'], queryFn: () => warehousesApi.list().then(r => r.data) })
  const { data: locations = [] } = useQuery({ queryKey: ['locations', selectedWH], queryFn: () => warehousesApi.listLocations(selectedWH ? { warehouse_id: selectedWH } : undefined).then(r => r.data) })

  const createWH = useMutation({
    mutationFn: (d: any) => warehousesApi.create(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['warehouses'] }); toast.success('Warehouse created'); setShowWHForm(false); setWhForm({ name: '', code: '', address: '' }) },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Failed'),
  })
  const createLoc = useMutation({
    mutationFn: (d: any) => warehousesApi.createLocation(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['locations'] }); toast.success('Location created'); setShowLocForm(false); setLocForm({ warehouse_id: '', name: '', code: '', description: '' }) },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Failed'),
  })

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Warehouses & Locations</h1>
        <div className="flex gap-3">
          <button onClick={() => setShowWHForm(true)} className="btn-secondary flex items-center gap-2"><Plus size={16} />New Warehouse</button>
          <button onClick={() => setShowLocForm(true)} className="btn-primary flex items-center gap-2"><Plus size={16} />New Location</button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Warehouses */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Warehouses</h2>
          {isLoading ? <LoadingSpinner /> : warehouses.length === 0 ? <EmptyState message="No warehouses yet" /> : (
            <div className="space-y-3">
              {warehouses.map((w: any) => (
                <div key={w.id} onClick={() => setSelectedWH(w.id === selectedWH ? null : w.id)}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${selectedWH === w.id ? 'border-blue-500 bg-blue-50' : 'border-gray-100 hover:border-gray-300'}`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-gray-900">{w.name}</p>
                      <p className="text-sm text-gray-500 font-mono">{w.code}</p>
                      {w.address && <p className="text-xs text-gray-400 mt-1">{w.address}</p>}
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${w.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-500'}`}>
                      {w.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Locations */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Locations {selectedWH && <span className="text-sm font-normal text-gray-500">— filtered by warehouse</span>}</h2>
          {locations.length === 0 ? <EmptyState message={selectedWH ? 'No locations in this warehouse' : 'Select a warehouse or view all'} /> : (
            <div className="space-y-2">
              {locations.map((l: any) => (
                <div key={l.id} className="p-3 rounded-lg border border-gray-100 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{l.name} <span className="font-mono text-xs text-gray-400">({l.code})</span></p>
                      <p className="text-xs text-gray-400">{l.warehouse?.name}</p>
                      {l.description && <p className="text-xs text-gray-400">{l.description}</p>}
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${l.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-500'}`}>
                      {l.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Warehouse Form Modal */}
      {showWHForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-5"><h2 className="text-lg font-bold">New Warehouse</h2><button onClick={() => setShowWHForm(false)}><X size={20} /></button></div>
            <form onSubmit={e => { e.preventDefault(); createWH.mutate(whForm) }} className="space-y-3">
              <div><label className="form-label">Name</label><input className="form-input" value={whForm.name} onChange={e => setWhForm(f => ({...f, name: e.target.value}))} required /></div>
              <div><label className="form-label">Code</label><input className="form-input uppercase" value={whForm.code} onChange={e => setWhForm(f => ({...f, code: e.target.value.toUpperCase()}))} required placeholder="WH01" /></div>
              <div><label className="form-label">Address</label><textarea className="form-input" value={whForm.address} onChange={e => setWhForm(f => ({...f, address: e.target.value}))} rows={2} /></div>
              <div className="flex justify-end gap-3"><button type="button" onClick={() => setShowWHForm(false)} className="btn-secondary">Cancel</button><button type="submit" className="btn-primary" disabled={createWH.isPending}>Create</button></div>
            </form>
          </div>
        </div>
      )}

      {/* Location Form Modal */}
      {showLocForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-5"><h2 className="text-lg font-bold">New Location</h2><button onClick={() => setShowLocForm(false)}><X size={20} /></button></div>
            <form onSubmit={e => { e.preventDefault(); createLoc.mutate({...locForm, warehouse_id: Number(locForm.warehouse_id)}) }} className="space-y-3">
              <div><label className="form-label">Warehouse</label>
                <select className="form-select" value={locForm.warehouse_id} onChange={e => setLocForm(f => ({...f, warehouse_id: e.target.value}))} required>
                  <option value="">Select warehouse</option>
                  {warehouses.map((w: any) => <option key={w.id} value={w.id}>{w.name} ({w.code})</option>)}
                </select>
              </div>
              <div><label className="form-label">Name</label><input className="form-input" value={locForm.name} onChange={e => setLocForm(f => ({...f, name: e.target.value}))} required /></div>
              <div><label className="form-label">Code</label><input className="form-input" value={locForm.code} onChange={e => setLocForm(f => ({...f, code: e.target.value}))} required placeholder="A01" /></div>
              <div><label className="form-label">Description</label><textarea className="form-input" value={locForm.description} onChange={e => setLocForm(f => ({...f, description: e.target.value}))} rows={2} /></div>
              <div className="flex justify-end gap-3"><button type="button" onClick={() => setShowLocForm(false)} className="btn-secondary">Cancel</button><button type="submit" className="btn-primary" disabled={createLoc.isPending}>Create</button></div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
